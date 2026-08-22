"""Minimal JUnit XML serializer for CI."""

from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement

from model_preflight.core.enums import StageStatus
from model_preflight.core.results import PreflightReport


def write_junit(report: PreflightReport, path: str | Path) -> None:
    suite = Element(
        "testsuite",
        {
            "name": "model-preflight",
            "tests": str(len(report.stages)),
            "failures": str(sum(stage.status is StageStatus.FAIL for stage in report.stages)),
            "errors": str(
                sum(stage.status is StageStatus.INTERNAL_ERROR for stage in report.stages)
            ),
            "skipped": str(
                sum(
                    stage.status in {StageStatus.INCONCLUSIVE, StageStatus.SKIPPED}
                    for stage in report.stages
                )
            ),
        },
    )
    for stage in report.stages:
        case = SubElement(
            suite,
            "testcase",
            {"name": stage.name, "time": f"{stage.duration_seconds:.6f}"},
        )
        message = "\n".join(f"{item.code}: {item.message}" for item in stage.diagnostics)
        if stage.status is StageStatus.FAIL:
            SubElement(case, "failure", {"message": message or "candidate failure"}).text = message
        elif stage.status is StageStatus.INTERNAL_ERROR:
            SubElement(case, "error", {"message": message or "checker error"}).text = message
        elif stage.status in {StageStatus.INCONCLUSIVE, StageStatus.SKIPPED}:
            SubElement(case, "skipped", {"message": message or stage.status.value})
    ElementTree(suite).write(Path(path), encoding="utf-8", xml_declaration=True)
