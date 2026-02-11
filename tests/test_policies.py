from ai_decision_router.models import ModelSpec
from ai_decision_router.policies import RulesPolicy, ScorePolicy

MODELS = [
    ModelSpec("fast", "mock", 0.6, 0.001, 100),
    ModelSpec("balanced", "mock", 0.8, 0.003, 500),
    ModelSpec("premium", "mock", 0.93, 0.009, 900),
]


def test_rules_policy_prefers_quality_for_code() -> None:
    decision = RulesPolicy().choose(
        "Write python code", "code", MODELS, budget_cost=1, budget_latency=2000
    )
    assert decision.model_name == "premium"


def test_score_policy_selects_viable_model() -> None:
    policy = ScorePolicy(quality_weight=0.7, cost_weight=0.2, latency_weight=0.1)
    decision = policy.choose(
        "General question", "chat/general", MODELS, budget_cost=0.02, budget_latency=700
    )
    assert decision.model_name == "balanced"
