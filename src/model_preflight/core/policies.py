"""Final status and scheduler recommendation policy."""

from model_preflight.core.diagnostics import Diagnostic
from model_preflight.core.enums import Classification, OverallStatus, PolicyMode, Severity


def status_from_diagnostics(diagnostics: list[Diagnostic]) -> OverallStatus:
    if any(item.classification is Classification.CHECKER_ERROR for item in diagnostics):
        return OverallStatus.INTERNAL_ERROR
    if any(
        item.classification is Classification.CONFIRMED and item.severity is Severity.ERROR
        for item in diagnostics
    ):
        return OverallStatus.FAIL
    if any(item.classification is Classification.INCONCLUSIVE for item in diagnostics):
        return OverallStatus.INCONCLUSIVE
    return OverallStatus.PASS


def submission_recommendation(status: OverallStatus, mode: PolicyMode) -> bool:
    if mode is PolicyMode.AUDIT:
        return True
    if mode is PolicyMode.BALANCED:
        return status in {OverallStatus.PASS, OverallStatus.INCONCLUSIVE}
    return status is OverallStatus.PASS
