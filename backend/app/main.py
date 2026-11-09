"""FastAPI application entry point: `uv run fastapi dev` (or `uv run uvicorn app.main:app`)."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.services.container import Services

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    services = Services.create(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        services.batches.shutdown()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Instagram quote videos and posts with AI-written quotes and captions.",
        lifespan=lifespan,
    )
    app.state.services = services

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    app.include_router(api_router)

    app.mount("/media/backgrounds", StaticFiles(directory=settings.backgrounds_dir), "backgrounds")
    app.mount("/media/videos", StaticFiles(directory=settings.videos_dir), "videos")
    app.mount("/media/posts", StaticFiles(directory=settings.posts_dir), "posts")

    @app.get("/", include_in_schema=False)
    def root() -> dict:
        return {"app": settings.app_name, "version": settings.version, "docs": "/docs"}

    return app


app = create_app()
