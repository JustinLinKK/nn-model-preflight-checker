"""Framework-backend protocol for abstract execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class AbstractResult:
    backend: str
    supported: bool
    evidence: dict[str, Any] = field(default_factory=dict)


class AbstractExecutionBackend(Protocol):
    def supports(self, candidate: Any, scenario: dict[str, Any]) -> bool: ...

    def execute(self, candidate: Any, scenario: dict[str, Any]) -> AbstractResult: ...
