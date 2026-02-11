from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ModelSpec, RoutingDecision


class BasePolicy(ABC):
    name: str

    @abstractmethod
    def choose(
        self,
        prompt: str,
        task_type: str,
        models: list[ModelSpec],
        budget_cost: float,
        budget_latency: float,
    ) -> RoutingDecision:
        raise NotImplementedError


def _estimate_cost(prompt: str, model: ModelSpec) -> float:
    token_estimate = max(20, len(prompt.split()) * 3)
    return token_estimate / 1000 * model.expected_cost_per_1k_tokens


class RulesPolicy(BasePolicy):
    name = "rules"

    def choose(
        self,
        prompt: str,
        task_type: str,
        models: list[ModelSpec],
        budget_cost: float,
        budget_latency: float,
    ) -> RoutingDecision:
        if not models:
            raise ValueError("No models available")
        length = len(prompt)

        candidates = []
        for m in models:
            est_cost = _estimate_cost(prompt, m)
            if est_cost <= budget_cost and m.expected_latency_ms <= budget_latency:
                candidates.append((m, est_cost))

        if not candidates:
            fallback = min(models, key=lambda m: m.expected_cost_per_1k_tokens)
            cost = _estimate_cost(prompt, fallback)
            return RoutingDecision(
                model_name=fallback.name,
                policy=self.name,
                task_type=task_type,
                rationale="No candidate met budget; picked cheapest model.",
                expected_quality=fallback.expected_quality,
                expected_cost=cost,
                expected_latency_ms=fallback.expected_latency_ms,
            )

        if task_type == "code":
            chosen, cost = max(candidates, key=lambda x: x[0].expected_quality)
            rationale = "Code tasks prioritize quality within budget."
        elif task_type == "writing" and length < 400:
            chosen, cost = min(candidates, key=lambda x: x[0].expected_latency_ms)
            rationale = "Short writing prompt prioritized low latency."
        elif task_type == "data":
            chosen, cost = min(candidates, key=lambda x: x[1])
            rationale = "Data tasks default to lower estimated cost."
        else:
            chosen, cost = sorted(candidates, key=lambda x: abs(x[0].expected_quality - 0.8))[0]
            rationale = "Balanced default selection by expected quality target."

        return RoutingDecision(
            model_name=chosen.name,
            policy=self.name,
            task_type=task_type,
            rationale=rationale,
            expected_quality=chosen.expected_quality,
            expected_cost=cost,
            expected_latency_ms=chosen.expected_latency_ms,
        )


class ScorePolicy(BasePolicy):
    name = "score"

    def __init__(self, quality_weight: float, cost_weight: float, latency_weight: float) -> None:
        self.quality_weight = quality_weight
        self.cost_weight = cost_weight
        self.latency_weight = latency_weight

    def choose(
        self,
        prompt: str,
        task_type: str,
        models: list[ModelSpec],
        budget_cost: float,
        budget_latency: float,
    ) -> RoutingDecision:
        if not models:
            raise ValueError("No models available")

        viable: list[tuple[ModelSpec, float, float]] = []
        for model in models:
            est_cost = _estimate_cost(prompt, model)
            if est_cost <= budget_cost and model.expected_latency_ms <= budget_latency:
                utility = (
                    self.quality_weight * model.expected_quality
                    - self.cost_weight * est_cost
                    - self.latency_weight * (model.expected_latency_ms / 1000)
                )
                if task_type == "reasoning":
                    utility += 0.05 * model.expected_quality
                viable.append((model, est_cost, utility))

        if not viable:
            cheapest = min(models, key=lambda m: m.expected_cost_per_1k_tokens)
            cost = _estimate_cost(prompt, cheapest)
            return RoutingDecision(
                model_name=cheapest.name,
                policy=self.name,
                task_type=task_type,
                rationale="No model fit budget constraints; used cheapest fallback.",
                expected_quality=cheapest.expected_quality,
                expected_cost=cost,
                expected_latency_ms=cheapest.expected_latency_ms,
            )

        chosen, cost, utility = max(viable, key=lambda v: v[2])
        return RoutingDecision(
            model_name=chosen.name,
            policy=self.name,
            task_type=task_type,
            rationale=(
                f"Selected via utility score={utility:.3f} using weights "
                f"q={self.quality_weight}, c={self.cost_weight}, l={self.latency_weight}."
            ),
            expected_quality=chosen.expected_quality,
            expected_cost=cost,
            expected_latency_ms=chosen.expected_latency_ms,
        )
