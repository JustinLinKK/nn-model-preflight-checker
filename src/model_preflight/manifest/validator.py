"""Semantic manifest validation."""

from pathlib import Path

from model_preflight.core.exceptions import ManifestError


def validate_paths(candidate_root: Path, fixture_root: Path | None) -> None:
    if not candidate_root.exists():
        raise ManifestError(f"candidate.root does not exist: {candidate_root}")
    if not candidate_root.is_dir():
        raise ManifestError(f"candidate.root is not a directory: {candidate_root}")
    if fixture_root is not None and not fixture_root.exists():
        raise ManifestError(f"task.fixture_root does not exist: {fixture_root}")


def validate_thresholds(warning: float, high_risk: float, failure: float | None) -> None:
    values = [warning, high_risk, *(value for value in [failure] if value is not None)]
    if any(value <= 0 for value in values):
        raise ManifestError("memory policy thresholds must be greater than zero")
    if warning >= high_risk:
        raise ManifestError("memory_warning_fraction must be lower than memory_high_risk_fraction")
    if failure is not None and high_risk > failure:
        raise ManifestError("memory_failure_fraction must not be below memory_high_risk_fraction")

