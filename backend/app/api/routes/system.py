from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.deps import ServicesDep
from app.core.catalog import ASPECT_FORMATS, AUTHORS, THEMES, Placement
from app.schemas.system import (
    AppConfig,
    AspectOption,
    BackgroundOption,
    FontOption,
    HealthResponse,
)

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(services: ServicesDep) -> HealthResponse:
    return HealthResponse(status="ok", version=services.settings.version)


@router.get("/config", response_model=AppConfig)
def config(services: ServicesDep) -> AppConfig:
    settings = services.settings
    models = list(dict.fromkeys([settings.groq_model, *settings.groq_models]))
    return AppConfig(
        version=settings.version,
        groq_configured=settings.groq_configured,
        default_model=settings.groq_model,
        models=models,
        themes=THEMES,
        authors=AUTHORS,
        aspect_ratios=[
            AspectOption(key=f.key, label=f.label, width=f.width, height=f.height)
            for f in ASPECT_FORMATS.values()
        ],
        placements=[p.value for p in Placement],
        fonts=[FontOption(id=f.id, name=f.name, family=f.family) for f in services.assets.fonts()],
        backgrounds=[
            BackgroundOption(
                id=b.id,
                name=b.name,
                url=f"/media/backgrounds/{b.id}",
                thumbnail_url=f"/api/backgrounds/{b.id}/thumbnail",
            )
            for b in services.assets.backgrounds()
        ],
        stats=services.library.stats(),
    )


@router.get("/backgrounds/{background_id}/thumbnail", response_class=FileResponse)
def background_thumbnail(background_id: str, services: ServicesDep) -> FileResponse:
    return FileResponse(
        services.assets.thumbnail(background_id),
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"},
    )
