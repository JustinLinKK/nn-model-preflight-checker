"""Stable built-in stage registry."""

from model_preflight.core.enums import StageName

STAGE_ORDER = (
    StageName.STATIC_SOURCE.value,
    StageName.HARDWARE.value,
    StageName.CONSTRUCTION.value,
    StageName.DATA_CONTRACT.value,
    StageName.ABSTRACT_FORWARD.value,
    StageName.CPU_TRAINING.value,
    StageName.VALIDATION.value,
    StageName.MEMORY.value,
)


def validate_stage_names(stages: set[str]) -> None:
    unknown = stages - set(STAGE_ORDER)
    if unknown:
        raise ValueError(f"unknown preflight stage(s): {', '.join(sorted(unknown))}")
