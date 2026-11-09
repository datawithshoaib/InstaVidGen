from typing import Annotated

from fastapi import Depends, Header, Request

from app.services.container import Services


def get_services(request: Request) -> Services:
    return request.app.state.services


def get_groq_api_key(
    x_groq_api_key: Annotated[str | None, Header(description="Optional per-user Groq key.")] = None,
) -> str | None:
    return (x_groq_api_key or "").strip() or None


ServicesDep = Annotated[Services, Depends(get_services)]
GroqKeyDep = Annotated[str | None, Depends(get_groq_api_key)]
