from __future__ import annotations

import re

TASK_TYPES = ["code", "reasoning", "data", "writing", "chat/general"]


def classify_task(prompt: str) -> str:
    text = prompt.lower().strip()
    if not text:
        return "chat/general"

    code_patterns = [r"```", r"\bpython\b", r"\bjava\b", r"\bdebug\b", r"\bfunction\b"]
    reasoning_patterns = [r"\bwhy\b", r"\bprove\b", r"\bstep by step\b", r"\blogic\b"]
    data_patterns = [r"\bcsv\b", r"\btable\b", r"\bquery\b", r"\bsql\b", r"\bdata\b"]
    writing_patterns = [r"\bblog\b", r"\bessay\b", r"\brewrite\b", r"\btone\b", r"\bsummary\b"]

    if any(re.search(p, text) for p in code_patterns):
        return "code"
    if any(re.search(p, text) for p in data_patterns):
        return "data"
    if any(re.search(p, text) for p in reasoning_patterns):
        return "reasoning"
    if any(re.search(p, text) for p in writing_patterns):
        return "writing"
    return "chat/general"
