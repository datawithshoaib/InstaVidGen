# Rendering is CPU-bound, so these are sync endpoints (FastAPI runs them in a threadpool).
from fastapi import APIRouter, status

from app.api.deps import ServicesDep
from app.schemas.media import MediaItem
from app.schemas.render import ComposeRequest, PostRequest, PreviewResponse, VideoRequest

router = APIRouter(prefix="/render", tags=["render"])


@router.post("/preview", response_model=PreviewResponse)
def preview(req: ComposeRequest, services: ServicesDep) -> PreviewResponse:
    return services.renderer.preview(req)


@router.post("/post", response_model=MediaItem, status_code=status.HTTP_201_CREATED)
def render_post(req: PostRequest, services: ServicesDep) -> MediaItem:
    return services.renderer.post(req)


@router.post("/video", response_model=MediaItem, status_code=status.HTTP_201_CREATED)
def render_video(req: VideoRequest, services: ServicesDep) -> MediaItem:
    return services.renderer.video(req)
