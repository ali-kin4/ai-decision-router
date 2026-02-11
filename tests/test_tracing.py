import json
from pathlib import Path

from ai_decision_router.tracing import TraceLogger


def test_trace_logger_writes_jsonl(tmp_path: Path) -> None:
    trace_file = tmp_path / "trace.jsonl"
    logger = TraceLogger(str(trace_file), enabled=True)
    logger.log("hello", {"policy": "rules", "chosen_model": "mock-fast"})

    lines = trace_file.read_text(encoding="utf-8").strip().splitlines()
    row = json.loads(lines[0])
    assert row["policy"] == "rules"
    assert row["chosen_model"] == "mock-fast"
    assert "prompt_hash" in row
