from pathlib import Path

from ai_decision_router.config import RouterConfig


def test_config_loading(tmp_path: Path) -> None:
    config_file = tmp_path / "router.toml"
    config_file.write_text(
        """
default_adapter = "mock"
enable_cache = true

[budgets]
max_cost_usd = 0.02
max_latency_ms = 1200

[policy]
name = "score"
quality_weight = 0.7
cost_weight = 0.2
latency_weight = 0.1

[[model_registry]]
name = "mock-fast"
provider = "mock"
expected_quality = 0.7
expected_cost_per_1k_tokens = 0.002
expected_latency_ms = 200
""",
        encoding="utf-8",
    )
    cfg = RouterConfig.from_toml(config_file)
    assert cfg.policy.name == "score"
    assert cfg.model_registry[0].name == "mock-fast"
