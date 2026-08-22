"""Controller context shared across stage orchestration."""

from dataclasses import dataclass
from typing import Any

from model_preflight.manifest.models import Manifest


@dataclass(frozen=True)
class EngineContext:
    manifest: Manifest
    target_profile: dict[str, Any]
    candidate_hash: str
    fixture_hash: str

