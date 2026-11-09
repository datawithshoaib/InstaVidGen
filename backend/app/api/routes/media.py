from fastapi import APIRouter, status

from app.api.deps import ServicesDep
from app.core.catalog import MediaKind
from app.schemas.media import MediaItem

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=list[MediaItem])
def list_media(services: ServicesDep, kind: MediaKind | None = None) -> list[MediaItem]:
    return services.library.list(kind)


@router.delete("/{kind}/{filename}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(kind: MediaKind, filename: str, services: ServicesDep) -> None:
    services.library.delete(kind, filename)
