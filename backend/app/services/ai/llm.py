"""Chat model factory (LangChain + Groq) and provider error translation."""

from collections.abc import Iterator
from contextlib import contextmanager

import groq
from langchain_groq import ChatGroq
from pydantic import SecretStr

from app.core.config import Settings
from app.core.errors import AIConfigurationError, AIRateLimitError, AIServiceError


def resolve_model(settings: Settings, model: str | None) -> str:
    return (model or "").strip() or settings.groq_model


def build_chat_model(settings: Settings, *, api_key: str | None, model: str | None) -> ChatGroq:
    """Create a ChatGroq client. A per-request key takes precedence over the env key."""
    key = (api_key or "").strip()
    if not key and settings.groq_api_key:
        key = settings.groq_api_key.get_secret_value().strip()
    if not key:
        raise AIConfigurationError(
            "No Groq API key configured. Add GROQ_API_KEY to backend/.env "
            "or enter a key in Settings."
        )

    model_name = resolve_model(settings, model)
    extra: dict = {}
    if model_name.startswith("openai/gpt-oss"):
        # Short creative outputs don't benefit from long reasoning; keep latency low.
        extra["reasoning_effort"] = "low"
    elif model_name.startswith("qwen/"):
        extra["reasoning_format"] = "hidden"

    return ChatGroq(
        model=model_name,
        api_key=SecretStr(key),
        temperature=settings.groq_temperature,
        timeout=settings.groq_timeout_seconds,
        max_retries=2,
        **extra,
    )


@contextmanager
def provider_errors() -> Iterator[None]:
    """Translate Groq SDK exceptions into user-facing domain errors."""
    try:
        yield
    except groq.AuthenticationError as exc:
        raise AIConfigurationError("Groq rejected the API key. Check it in Settings.") from exc
    except groq.PermissionDeniedError as exc:
        raise AIConfigurationError(
            "Your Groq account does not have access to this model. Pick another model in Settings."
        ) from exc
    except groq.NotFoundError as exc:
        raise AIConfigurationError(
            "The selected Groq model was not found. Pick another model in Settings."
        ) from exc
    except groq.RateLimitError as exc:
        raise AIRateLimitError("Groq rate limit reached. Wait a moment and try again.") from exc
    except groq.APIConnectionError as exc:
        raise AIServiceError("Could not reach Groq. Check your internet connection.") from exc
    except groq.APIStatusError as exc:
        raise AIServiceError(f"Groq request failed: {exc.message}") from exc
