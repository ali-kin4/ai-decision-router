import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class BudgetConfig(BaseModel):
    max_cost_usd: float = 0.05
    max_latency_ms: float = 2500.0


class PolicyConfig(BaseModel):
    name: str = "rules"
    quality_weight: float = 0.6
    cost_weight: float = 0.2
    latency_weight: float = 0.2


class ModelConfig(BaseModel):
    name: str
    provider: str = "mock"
    expected_quality: float = 0.7
    expected_cost_per_1k_tokens: float = 0.002
    expected_latency_ms: float = 400.0
    max_context_tokens: int = 8192


class TraceConfig(BaseModel):
    enabled: bool = True
    output_path: str = "traces/router_traces.jsonl"


class RouterConfig(BaseModel):
    default_adapter: str = "mock"
    enable_cache: bool = True
    budgets: BudgetConfig = Field(default_factory=BudgetConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    trace: TraceConfig = Field(default_factory=TraceConfig)
    model_registry: list[ModelConfig] = Field(default_factory=list)

    @classmethod
    def from_toml(cls, path: str | Path) -> "RouterConfig":
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)


def default_config() -> "RouterConfig":
    return RouterConfig(
        model_registry=[
            ModelConfig(
                name="mock-fast",
                provider="mock",
                expected_quality=0.68,
                expected_cost_per_1k_tokens=0.001,
                expected_latency_ms=180,
            ),
            ModelConfig(
                name="mock-balanced",
                provider="mock",
                expected_quality=0.80,
                expected_cost_per_1k_tokens=0.003,
                expected_latency_ms=500,
            ),
            ModelConfig(
                name="mock-premium",
                provider="mock",
                expected_quality=0.92,
                expected_cost_per_1k_tokens=0.009,
                expected_latency_ms=950,
            ),
        ]
    )
