#!/usr/bin/env python3
"""Record checker results and runtime versions for compatibility-matrix jobs."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
from pathlib import Path
from typing import Any

from model_preflight import check


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="append", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    results: list[dict[str, Any]] = []
    for manifest in args.manifest:
        report = check(manifest, use_cache=False)
        results.append(
            {
                "manifest": str(manifest.resolve()),
                "candidate_id": report.candidate_id,
                "status": report.overall_status.value,
                "diagnostic_codes": sorted({item.code for item in report.diagnostics}),
            }
        )
    value = {
        "python": platform.python_version(),
        "torch": importlib.metadata.version("torch"),
        "checker": importlib.metadata.version("model-preflight"),
        "results": results,
    }
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 1 if any(item["status"] in {"FAIL", "INTERNAL_ERROR"} for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())

