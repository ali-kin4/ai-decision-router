from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    name: str
    provider: str
    expected_quality: float
    expected_cost_per_1k_tokens: float
    expected_latency_ms: float
    max_context_tokens: int = 8192
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RoutingDecision:
    model_name: str
    policy: str
    task_type: str
    rationale: str
    expected_quality: float
    expected_cost: float
    expected_latency_ms: float


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_name: str
    latency_ms: float
    estimated_cost_usd: float
    metadata: dict[str, Any] = field(default_factory=dict)
