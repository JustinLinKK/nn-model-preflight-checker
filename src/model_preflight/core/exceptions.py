"""Expected checker exceptions."""


class PreflightError(Exception):
    """Base class for controlled preflight failures."""


class ManifestError(PreflightError):
    """The manifest is missing, malformed, or semantically invalid."""


class WorkerProtocolError(PreflightError):
    """A worker returned an invalid protocol response."""


class ProfileError(PreflightError):
    """A target profile is invalid or cannot be found."""

