"""Content-addressed cache for complete deterministic reports."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from model_preflight.core.enums import OverallStatus
from model_preflight.core.results import PreflightReport


def cache_key(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class ResultCache:
    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
            root = base / "model-preflight" / "reports"
        self.root = root

    def load(self, key: str) -> PreflightReport | None:
        path = self.root / f"{key}.json"
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return PreflightReport.from_dict(value)
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def store(self, key: str, report: PreflightReport) -> None:
        if report.overall_status is OverallStatus.INTERNAL_ERROR:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"{key}.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)

