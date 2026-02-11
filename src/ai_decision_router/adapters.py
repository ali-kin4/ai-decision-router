from __future__ import annotations

import hashlib
import os
import time
from abc import ABC, abstractmethod

from .models import ModelResponse, ModelSpec


class BaseAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: ModelSpec) -> ModelResponse:
        raise NotImplementedError


class MockAdapter(BaseAdapter):
    def generate(self, prompt: str, model: ModelSpec) -> ModelResponse:
        seed = int(hashlib.sha256(f"{prompt}:{model.name}".encode()).hexdigest()[:8], 16)
        latency_ms = max(30, int(model.expected_latency_ms + (seed % 90) - 45))
        token_estimate = max(20, min(4000, len(prompt.split()) * 3))
        estimated_cost = (token_estimate / 1000) * model.expected_cost_per_1k_tokens
        text = (
            f"[mock:{model.name}] task handled with expected quality "
            f"{model.expected_quality:.2f}. prompt_tokens≈{token_estimate}."
        )
        return ModelResponse(
            text=text,
            model_name=model.name,
            latency_ms=float(latency_ms),
            estimated_cost_usd=estimated_cost,
            metadata={"token_estimate": token_estimate, "seed": seed},
        )


class OpenAIAdapter(BaseAdapter):
    """Structure-ready adapter. Network call intentionally stubbed for offline default usage."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def generate(self, prompt: str, model: ModelSpec) -> ModelResponse:
        start = time.perf_counter()
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Configure env vars to enable OpenAI adapter."
            )
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ModelResponse(
            text="OpenAIAdapter stub response: integrate provider SDK/API call here.",
            model_name=model.name,
            latency_ms=elapsed_ms,
            estimated_cost_usd=0.0,
            metadata={"base_url": self.base_url, "stub": True},
        )
