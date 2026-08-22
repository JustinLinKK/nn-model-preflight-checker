"""Stage composition helpers."""

from __future__ import annotations

from typing import Any

from model_preflight.core.enums import StageStatus
from model_preflight.core.results import StageResult


def combine_stage_results(name: str, results: list[StageResult]) -> StageResult:
    precedence = {
        StageStatus.PASS: 0,
        StageStatus.SKIPPED: 0,
        StageStatus.INCONCLUSIVE: 1,
        StageStatus.FAIL: 2,
        StageStatus.INTERNAL_ERROR: 3,
    }
    status = max(
        (item.status for item in results),
        key=lambda value: precedence[value],
        default=StageStatus.SKIPPED,
    )
    diagnostics = [diagnostic for item in results for diagnostic in item.diagnostics]
    scenarios: list[dict[str, Any]] = []
    for item in results:
        scenarios.append(
            {
                "status": item.status.value,
                "duration_seconds": round(item.duration_seconds, 6),
                **item.evidence,
            }
        )
    return StageResult(
        name=name,
        status=status,
        duration_seconds=sum(item.duration_seconds for item in results),
        diagnostics=diagnostics,
        evidence={"scenarios": scenarios},
    )
