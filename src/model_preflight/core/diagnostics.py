"""Stable structured diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model_preflight.core.enums import Classification, Severity


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: Severity
    stage: str
    classification: Classification
    message: str
    file: str | None = None
    line: int | None = None
    module: str | None = None
    operation: str | None = None
    scenario: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    exception_type: str | None = None
    stack_trace: str | None = None
    reproduction: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity.value,
            "stage": self.stage,
            "classification": self.classification.value,
            "message": self.message,
        }
        optional = {
            "file": self.file,
            "line": self.line,
            "module": self.module,
            "operation": self.operation,
            "exception_type": self.exception_type,
            "stack_trace": self.stack_trace,
            "reproduction": self.reproduction,
        }
        result.update({key: value for key, value in optional.items() if value is not None})
        if self.scenario:
            result["scenario"] = self.scenario
        if self.evidence:
            result["evidence"] = self.evidence
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Diagnostic:
        return cls(
            code=str(value["code"]),
            severity=Severity(value["severity"]),
            stage=str(value["stage"]),
            classification=Classification(value["classification"]),
            message=str(value["message"]),
            file=value.get("file"),
            line=value.get("line"),
            module=value.get("module"),
            operation=value.get("operation"),
            scenario=dict(value.get("scenario", {})),
            evidence=dict(value.get("evidence", {})),
            exception_type=value.get("exception_type"),
            stack_trace=value.get("stack_trace"),
            reproduction=value.get("reproduction"),
        )

