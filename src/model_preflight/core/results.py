"""Stage and final report models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model_preflight.core.diagnostics import Diagnostic
from model_preflight.core.enums import OverallStatus, StageStatus


@dataclass
class StageResult:
    name: str
    status: StageStatus
    duration_seconds: float = 0.0
    diagnostics: list[Diagnostic] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "status": self.status.value,
            "duration_seconds": round(self.duration_seconds, 6),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }
        if self.evidence:
            result["evidence"] = self.evidence
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> StageResult:
        return cls(
            name=str(value["name"]),
            status=StageStatus(value["status"]),
            duration_seconds=float(value.get("duration_seconds", 0.0)),
            diagnostics=[
                Diagnostic.from_dict(item) for item in value.get("diagnostics", [])
            ],
            evidence=dict(value.get("evidence", {})),
        )


@dataclass
class PreflightReport:
    candidate_id: str
    candidate_hash: str
    checker_version: str
    overall_status: OverallStatus
    gpu_submission_recommended: bool
    normalized_manifest: dict[str, Any]
    stages: list[StageResult]
    diagnostics: list[Diagnostic]
    gpu_check_required: bool = False
    environment: dict[str, Any] = field(default_factory=dict)
    resource_estimate: dict[str, Any] | None = None
    report_schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "report_schema_version": self.report_schema_version,
            "candidate_id": self.candidate_id,
            "candidate_hash": self.candidate_hash,
            "checker_version": self.checker_version,
            "overall_status": self.overall_status.value,
            "gpu_submission_recommended": self.gpu_submission_recommended,
            "gpu_check_required": self.gpu_check_required,
            "normalized_manifest": self.normalized_manifest,
            "stages": [stage.to_dict() for stage in self.stages],
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "environment": self.environment,
        }
        if self.resource_estimate is not None:
            value["resource_estimate"] = self.resource_estimate
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> PreflightReport:
        return cls(
            candidate_id=str(value["candidate_id"]),
            candidate_hash=str(value["candidate_hash"]),
            checker_version=str(value["checker_version"]),
            overall_status=OverallStatus(value["overall_status"]),
            gpu_submission_recommended=bool(value["gpu_submission_recommended"]),
            gpu_check_required=bool(value.get("gpu_check_required", False)),
            normalized_manifest=dict(value["normalized_manifest"]),
            stages=[StageResult.from_dict(item) for item in value.get("stages", [])],
            diagnostics=[
                Diagnostic.from_dict(item) for item in value.get("diagnostics", [])
            ],
            environment=dict(value.get("environment", {})),
            resource_estimate=(
                dict(value["resource_estimate"])
                if value.get("resource_estimate") is not None
                else None
            ),
            report_schema_version=int(value.get("report_schema_version", 1)),
        )
