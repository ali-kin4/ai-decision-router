from __future__ import annotations

from dataclasses import asdict

from .adapters import BaseAdapter, MockAdapter, OpenAIAdapter
from .classifier import classify_task
from .config import RouterConfig, default_config
from .models import ModelSpec, RoutingDecision
from .policies import BasePolicy, RulesPolicy, ScorePolicy
from .tracing import TraceLogger


class DecisionRouter:
    def __init__(self, config: RouterConfig | None = None) -> None:
        self.config = config or default_config()
        self.models: dict[str, ModelSpec] = {
            m.name: ModelSpec(
                name=m.name,
                provider=m.provider,
                expected_quality=m.expected_quality,
                expected_cost_per_1k_tokens=m.expected_cost_per_1k_tokens,
                expected_latency_ms=m.expected_latency_ms,
                max_context_tokens=m.max_context_tokens,
            )
            for m in self.config.model_registry
        }
        self.trace = TraceLogger(self.config.trace.output_path, enabled=self.config.trace.enabled)
        self._cache: dict[str, dict] = {}

    def _adapter(self, provider: str) -> BaseAdapter:
        if provider == "openai":
            return OpenAIAdapter()
        return MockAdapter()

    def _policy(self) -> BasePolicy:
        policy_name = self.config.policy.name.lower()
        if policy_name == "score":
            return ScorePolicy(
                quality_weight=self.config.policy.quality_weight,
                cost_weight=self.config.policy.cost_weight,
                latency_weight=self.config.policy.latency_weight,
            )
        return RulesPolicy()

    def explain(self, prompt: str) -> RoutingDecision:
        task_type = classify_task(prompt)
        return self._policy().choose(
            prompt=prompt,
            task_type=task_type,
            models=list(self.models.values()),
            budget_cost=self.config.budgets.max_cost_usd,
            budget_latency=self.config.budgets.max_latency_ms,
        )

    def run(self, prompt: str) -> dict:
        if self.config.enable_cache and prompt in self._cache:
            cached = {**self._cache[prompt], "cache_hit": True}
            self.trace.log(prompt, {**cached, "cached": True})
            return cached

        decision = self.explain(prompt)
        model = self.models[decision.model_name]
        adapter = self._adapter(model.provider)
        response = adapter.generate(prompt, model)

        result = {
            "task_type": decision.task_type,
            "policy": decision.policy,
            "chosen_model": decision.model_name,
            "rationale": decision.rationale,
            "response": response.text,
            "latency_ms": response.latency_ms,
            "est_cost": response.estimated_cost_usd,
            "metadata": response.metadata,
            "cache_hit": False,
        }
        self.trace.log(prompt, {**asdict(decision), **result})
        if self.config.enable_cache:
            self._cache[prompt] = result
        return result
