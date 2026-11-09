"""Custom exceptions."""


class StudentAppError(Exception):
    """Base class of all application errors."""


class ValidationError(StudentAppError):
    """Business rule is violated; ``field`` names the invalid field."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


class ImportDataError(StudentAppError):
    """Input data cannot be imported; ``line_number`` points to the record."""

    def __init__(self, message: str, *, line_number: int | None = None) -> None:
        super().__init__(message)
        self.line_number = line_number


class ExportError(StudentAppError):
    """Output cannot be written."""


class NotFoundError(StudentAppError):
    """Requested entity does not exist."""


class NotificationError(StudentAppError):
    """Notification cannot be delivered."""


class ConfigurationError(StudentAppError):
    """Configuration is missing or invalid."""
