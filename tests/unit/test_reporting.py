from pathlib import Path

from model_preflight.api import check
from model_preflight.reporting.json_report import render_json, validate_report

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_json_report_is_schema_valid_and_deterministic() -> None:
    report = check(FIXTURES / "valid.yaml", only={"static_source", "hardware"})
    validate_report(report)
    assert render_json(report) == render_json(report)
    assert '"overall_status": "PASS"' in render_json(report)

