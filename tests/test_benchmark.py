from pathlib import Path

from ai_decision_router.benchmark import SUITES, run_benchmark
from ai_decision_router.config import default_config
from ai_decision_router.router import DecisionRouter


def test_benchmark_empty_suite(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    SUITES["empty"] = str(empty)
    try:
        report = run_benchmark(DecisionRouter(default_config()), "empty")

        assert report["num_prompts"] == 0
        assert report["classifier_accuracy"] == 0.0
        assert report["avg_est_cost"] == 0.0
        assert report["avg_latency_ms"] == 0.0
        assert report["avg_quality_proxy"] == 0.0
    finally:
        del SUITES["empty"]
