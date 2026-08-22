from model_preflight.core.diagnostics import Diagnostic
from model_preflight.core.enums import (
    Classification,
    OverallStatus,
    PolicyMode,
    Severity,
)
from model_preflight.core.policies import status_from_diagnostics, submission_recommendation


def diagnostic(classification: Classification) -> Diagnostic:
    return Diagnostic(
        code="CHK001",
        severity=Severity.ERROR,
        stage="test",
        classification=classification,
        message="test",
    )


def test_status_precedence() -> None:
    assert status_from_diagnostics([]) is OverallStatus.PASS
    assert (
        status_from_diagnostics([diagnostic(Classification.INCONCLUSIVE)])
        is OverallStatus.INCONCLUSIVE
    )
    assert (
        status_from_diagnostics([diagnostic(Classification.CONFIRMED)])
        is OverallStatus.FAIL
    )
    assert (
        status_from_diagnostics(
            [
                diagnostic(Classification.CONFIRMED),
                diagnostic(Classification.CHECKER_ERROR),
            ]
        )
        is OverallStatus.INTERNAL_ERROR
    )


def test_policy_recommendations() -> None:
    assert submission_recommendation(OverallStatus.FAIL, PolicyMode.AUDIT)
    assert submission_recommendation(OverallStatus.INCONCLUSIVE, PolicyMode.BALANCED)
    assert not submission_recommendation(OverallStatus.FAIL, PolicyMode.BALANCED)
    assert not submission_recommendation(OverallStatus.INCONCLUSIVE, PolicyMode.STRICT)

