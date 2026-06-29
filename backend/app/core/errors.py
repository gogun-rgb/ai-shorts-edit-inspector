from __future__ import annotations


class UserFacingError(Exception):
    """An expected error that can be safely shown to the user."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ToolUnavailableError(UserFacingError):
    """Raised when a local binary such as FFmpeg is not available."""


class AnalysisNotFoundError(UserFacingError):
    """Raised when an analysis id does not exist."""

