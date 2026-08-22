"""Deterministic JSON report serialization."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

import jsonschema

from model_preflight.core.results import PreflightReport


def report_schema() -> dict[str, Any]:
    resource = files("model_preflight.reporting").joinpath("schema_v1.json")
    return cast(dict[str, Any], json.loads(resource.read_text(encoding="utf-8")))


def validate_report(report: PreflightReport) -> None:
    jsonschema.Draft202012Validator(report_schema()).validate(report.to_dict())


def render_json(report: PreflightReport) -> str:
    validate_report(report)
    return json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(report: PreflightReport, path: str | Path) -> None:
    Path(path).write_text(render_json(report), encoding="utf-8")
