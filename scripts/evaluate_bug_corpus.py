#!/usr/bin/env python3
"""Replay labeled historical candidates and report checker quality metrics."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Any

from model_preflight import check
from model_preflight.core.exceptions import ManifestError
from model_preflight.reporting.json_report import validate_report


def percentile95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def evaluate(root: Path) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    for manifest in sorted(root.glob("*" + "/preflight.yaml")):
        expected_path = manifest.with_name("expected.json")
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        started = time.monotonic()
        try:
            report = check(manifest, use_cache=False)
            validate_report(report)
            status = report.overall_status.value
            codes = sorted({item.code for item in report.diagnostics})
        except ManifestError as exc:
            status = "INVALID_MANIFEST"
            codes = []
            controller_error = str(exc)
        except Exception as exc:  # Evaluation must retain all samples.
            status = "INTERNAL_ERROR"
            codes = []
            controller_error = f"{type(exc).__name__}: {exc}"
        duration = time.monotonic() - started
        expected_status = expected["overall_status"]
        expected_codes = sorted(expected.get("diagnostic_codes", []))
        sample = {
            "name": manifest.parent.name,
            "ground_truth": expected.get("ground_truth", "unknown"),
            "expected_status": expected_status,
            "actual_status": status,
            "expected_codes": expected_codes,
            "actual_codes": codes,
            "status_match": status == expected_status,
            "codes_present": set(expected_codes).issubset(codes),
            "duration_seconds": round(duration, 6),
        }
        if "controller_error" in locals():
            sample["controller_error"] = controller_error
            del controller_error
        samples.append(sample)

    confirmed = [item for item in samples if item["expected_status"] == "FAIL"]
    non_failures = [item for item in samples if item["expected_status"] != "FAIL"]
    caught = [item for item in confirmed if item["actual_status"] == "FAIL"]
    false_rejections = [item for item in non_failures if item["actual_status"] == "FAIL"]
    durations = [float(item["duration_seconds"]) for item in samples]
    return {
        "samples": samples,
        "metrics": {
            "sample_count": len(samples),
            "confirmed_failure_count": len(confirmed),
            "confirmed_failures_caught": len(caught),
            "catch_rate": len(caught) / len(confirmed) if confirmed else None,
            "false_hard_rejections": len(false_rejections),
            "false_hard_rejection_rate": (
                len(false_rejections) / len(non_failures) if non_failures else None
            ),
            "inconclusive_count": sum(
                item["actual_status"] == "INCONCLUSIVE" for item in samples
            ),
            "internal_error_count": sum(
                item["actual_status"] == "INTERNAL_ERROR" for item in samples
            ),
            "median_latency_seconds": (
                statistics.median(durations) if durations else 0.0
            ),
            "p95_latency_seconds": percentile95(durations),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = evaluate(args.corpus.resolve())
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    mismatches = [
        item
        for item in result["samples"]
        if not item["status_match"] or not item["codes_present"]
    ]
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())

