"""Public Python API."""

from __future__ import annotations

from pathlib import Path

from model_preflight.core.exceptions import ManifestError, ProfileError
from model_preflight.core.results import PreflightReport
from model_preflight.engine.runner import PreflightRunner
from model_preflight.manifest.loader import load_manifest


def check(
    manifest_path: str | Path,
    *,
    only: set[str] | None = None,
    use_cache: bool | None = None,
) -> PreflightReport:
    """Run configured checks and return a schema-valid report."""
    manifest = load_manifest(manifest_path)
    try:
        return PreflightRunner(manifest, only=only, use_cache=use_cache).run()
    except ProfileError as exc:
        raise ManifestError(str(exc)) from exc
