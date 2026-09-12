"""Application-specific API exceptions."""


class ApiError(Exception):
    """An expected API failure that should use the standard JSON error format."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: list[dict] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
