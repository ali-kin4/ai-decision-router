from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TraceLogger:
    def __init__(self, output_path: str, enabled: bool = True) -> None:
        self.output_path = Path(output_path)
        self.enabled = enabled
        if self.enabled:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, prompt: str, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
            **payload,
        }
        with self.output_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
