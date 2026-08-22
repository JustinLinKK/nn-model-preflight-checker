"""Transparent analytical memory estimate."""

from __future__ import annotations

from typing import Any

from model_preflight.core.diagnostics import Diagnostic
from model_preflight.core.enums import Classification, Severity, StageName, StageStatus
from model_preflight.core.results import StageResult
from model_preflight.manifest.models import Manifest


def estimate_resources(
    manifest: Manifest,
    profile: dict[str, Any],
    construction: dict[str, Any],
    maximum_activation_bytes: int,
) -> tuple[StageResult, dict[str, Any]]:
    parameter_bytes = int(construction.get("parameter_bytes", 0))
    gradient_bytes = int(construction.get("trainable_parameter_bytes", parameter_bytes))
    optimizer_name = str(construction.get("optimizer_type", "")).lower()
    if "adam" in optimizer_name:
        optimizer_multiplier = 2
    elif "sgd" in optimizer_name:
        optimizer_multiplier = 1
    else:
        optimizer_multiplier = 2
    optimizer_state_bytes = gradient_bytes * optimizer_multiplier
    activation_bytes = int(maximum_activation_bytes)
    subtotal = parameter_bytes + gradient_bytes + optimizer_state_bytes + activation_bytes
    safety_margin_bytes = int(subtotal * 0.15)
    estimated_total = subtotal + safety_margin_bytes
    target_vram = int(profile["vram_bytes"])
    fraction = estimated_total / target_vram
    if fraction < manifest.policy.memory_warning_fraction:
        risk = "low"
    elif fraction < manifest.policy.memory_high_risk_fraction:
        risk = "warning"
    else:
        risk = "high"
    estimate = {
        "parameter_bytes_exact": parameter_bytes,
        "gradient_bytes_exact": gradient_bytes,
        "optimizer_state_bytes_estimated": optimizer_state_bytes,
        "saved_activation_bytes_estimated": activation_bytes,
        "safety_margin_bytes": safety_margin_bytes,
        "estimated_total_bytes": estimated_total,
        "target_vram_bytes": target_vram,
        "target_vram_fraction": round(fraction, 6),
        "estimated_risk": risk,
        "uncertainty_sources": [
            "allocator fragmentation",
            "tensor lifetime overlap",
            "cuDNN and compiler workspaces",
            "custom kernels",
            "activation checkpointing",
        ],
        "is_gpu_oom_guarantee": False,
    }
    diagnostics: list[Diagnostic] = []
    status = StageStatus.PASS
    if fraction >= manifest.policy.memory_warning_fraction:
        classification = Classification.RISK
        severity = Severity.WARNING
        if (
            manifest.policy.memory_failure_fraction is not None
            and fraction >= manifest.policy.memory_failure_fraction
        ):
            classification = Classification.INCONCLUSIVE
            severity = Severity.ERROR
            status = StageStatus.INCONCLUSIVE
        diagnostics.append(
            Diagnostic(
                code="MEM001",
                severity=severity,
                stage=StageName.MEMORY.value,
                classification=classification,
                message=(
                    f"analytical memory estimate is {fraction:.1%} of target VRAM "
                    f"({risk} estimated risk); this is not a CUDA OOM guarantee"
                ),
                evidence=estimate,
                reproduction="model-preflight check preflight.yaml --only memory",
            )
        )
    return (
        StageResult(
            name=StageName.MEMORY.value,
            status=status,
            diagnostics=diagnostics,
            evidence=estimate,
        ),
        estimate,
    )
