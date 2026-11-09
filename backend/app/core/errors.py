"""Domain errors, mapped to HTTP responses in `app.main`."""


class AppError(Exception):
    status_code: int = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class InvalidRequestError(AppError):
    status_code = 422


class AIConfigurationError(AppError):
    """No usable Groq API key / model configuration."""

    status_code = 400


class AIServiceError(AppError):
    """The LLM provider failed or returned unusable output."""

    status_code = 502


class AIRateLimitError(AIServiceError):
    status_code = 429


class RenderError(AppError):
    status_code = 500
