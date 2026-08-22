"""Stable public enumerations."""

from enum import Enum


class StrEnum(str, Enum):
    """Python 3.10-compatible string enum."""

    def __str__(self) -> str:
        return str(self.value)


class OverallStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Classification(StrEnum):
    CONFIRMED = "confirmed_candidate_failure"
    INCONCLUSIVE = "inconclusive"
    CHECKER_ERROR = "checker_error"
    RISK = "risk"
    INFORMATIONAL = "informational"


class PolicyMode(StrEnum):
    AUDIT = "audit"
    BALANCED = "balanced"
    STRICT = "strict"


class StageName(StrEnum):
    STATIC_SOURCE = "static_source"
    CONSTRUCTION = "construction"
    DATA_CONTRACT = "data_contract"
    ABSTRACT_FORWARD = "abstract_forward"
    CPU_TRAINING = "cpu_training"
    VALIDATION = "validation"
    HARDWARE = "hardware"
    MEMORY = "memory"


class StageStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SKIPPED = "SKIPPED"
