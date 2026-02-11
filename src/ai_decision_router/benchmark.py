from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .classifier import classify_task
from .router import DecisionRouter

SUITES = {
    "quick": "benchmarks/quick.json",
    "medium": "benchmarks/medium.json",
}


def run_benchmark(router: DecisionRouter, suite: str) -> dict:
    if suite not in SUITES:
        raise ValueError(f"Unknown suite: {suite}")
    prompts = json.loads(Path(SUITES[suite]).read_text(encoding="utf-8"))

    expected_matches = 0
    decisions = Counter()
    costs = []
    latencies = []
    quality_proxy = []

    for item in prompts:
        predicted = classify_task(item["prompt"])
        if predicted == item["expected_category"]:
            expected_matches += 1
        result = router.run(item["prompt"])
        decisions[result["chosen_model"]] += 1
        costs.append(result["est_cost"])
        latencies.append(result["latency_ms"])
        quality_proxy.append(
            next(m.expected_quality for m in router.models if m.name == result["chosen_model"])
        )

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "suite": suite,
        "num_prompts": len(prompts),
        "classifier_accuracy": expected_matches / len(prompts),
        "policy_distribution": dict(decisions),
        "avg_est_cost": sum(costs) / len(costs),
        "avg_latency_ms": sum(latencies) / len(latencies),
        "avg_quality_proxy": sum(quality_proxy) / len(quality_proxy),
    }
    _write_reports(report, suite)
    return report


def _write_reports(report: dict, suite: str) -> None:
    Path("reports").mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    json_path = Path(f"reports/{suite}-{ts}.json")
    md_path = Path(f"reports/{suite}-{ts}.md")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = (
        f"# Benchmark Report ({suite})\n\n"
        f"- prompts: {report['num_prompts']}\n"
        f"- classifier_accuracy: {report['classifier_accuracy']:.3f}\n"
        f"- avg_est_cost_usd: {report['avg_est_cost']:.6f}\n"
        f"- avg_latency_ms: {report['avg_latency_ms']:.1f}\n"
        f"- avg_quality_proxy: {report['avg_quality_proxy']:.3f}\n\n"
        "## Policy Distribution\n"
    )
    for model, count in report["policy_distribution"].items():
        md += f"- {model}: {count}\n"
    md_path.write_text(md, encoding="utf-8")
