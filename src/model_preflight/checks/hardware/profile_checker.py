"""Versioned, inspectable target-GPU capability checks."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

import jsonschema
import yaml

from model_preflight.core.diagnostics import Diagnostic
from model_preflight.core.enums import Classification, Severity, StageName, StageStatus
from model_preflight.core.exceptions import ProfileError
from model_preflight.core.results import StageResult
from model_preflight.manifest.models import Manifest


def _schema() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(
            files("model_preflight.profiles")
            .joinpath("schema.json")
            .read_text(encoding="utf-8")
        ),
    )


def _profile_path(manifest: Manifest) -> Path:
    name = manifest.target.profile
    supplied = Path(name).expanduser()
    if supplied.is_absolute() or supplied.suffix in {".yaml", ".yml"}:
        return (
            supplied.resolve()
            if supplied.is_absolute()
            else (manifest.source_path.parent / supplied).resolve()
        )
    resource = files("model_preflight.profiles").joinpath(f"{name}.yaml")
    return Path(str(resource))


def load_profile(manifest: Manifest) -> dict[str, Any]:
    path = _profile_path(manifest)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProfileError(f"cannot read target profile {manifest.target.profile}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProfileError(f"target profile is not a mapping: {path}")
    try:
        jsonschema.Draft202012Validator(_schema()).validate(value)
    except jsonschema.ValidationError as exc:
        location = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        raise ProfileError(f"target profile invalid at {location}: {exc.message}") from exc
    return value


def run_hardware_checks(manifest: Manifest, profile: dict[str, Any]) -> StageResult:
    diagnostics: list[Diagnostic] = []
    supported = set(profile["native_training_dtypes"])
    unsupported = set(profile["unsupported_features"])
    for precision in manifest.scenarios.precision:
        if precision not in supported or precision in unsupported:
            diagnostics.append(
                Diagnostic(
                    code="GPU001",
                    severity=Severity.ERROR,
                    stage=StageName.HARDWARE.value,
                    classification=Classification.CONFIRMED,
                    message=(
                        f"requested precision {precision!r} is unsupported by "
                        f"{profile['name']}"
                    ),
                    evidence={
                        "requested_precision": precision,
                        "native_training_dtypes": sorted(supported),
                        "target_profile": manifest.target.profile,
                    },
                    reproduction="model-preflight check preflight.yaml --only hardware",
                )
            )
    status = StageStatus.FAIL if diagnostics else StageStatus.PASS
    return StageResult(
        name=StageName.HARDWARE.value,
        status=status,
        diagnostics=diagnostics,
        evidence={
            "profile": manifest.target.profile,
            "name": profile["name"],
            "architecture": profile["architecture"],
            "compute_capability": profile["compute_capability"],
            "vram_bytes": profile["vram_bytes"],
            "profile_schema_version": profile["schema_version"],
        },
    )
