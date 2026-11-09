"""Render previews, posts and videos from API requests."""

import base64
from io import BytesIO

from app.core.catalog import ASPECT_FORMATS, MediaKind
from app.core.config import Settings
from app.schemas.media import MediaItem
from app.schemas.render import ComposeRequest, PostRequest, PreviewResponse, VideoRequest
from app.services.media.assets import AssetLibrary, Background
from app.services.media.composer import ComposeSpec, compose
from app.services.media.encoder import encode_still_video
from app.services.media.library import MediaLibrary

PREVIEW_MAX_WIDTH = 720


class RenderService:
    def __init__(self, settings: Settings, assets: AssetLibrary, library: MediaLibrary) -> None:
        self._settings = settings
        self._assets = assets
        self._library = library

    def _compose(self, req: ComposeRequest, background: Background):
        spec = ComposeSpec(
            background=background.path,
            quote=req.quote,
            aspect=ASPECT_FORMATS[req.aspect_ratio],
            font=self._assets.font_path(req.font_id),
            attribution_font=self._assets.attribution_font_path(),
            author=req.author,
            font_scale=req.font_scale,
            placement=req.placement,
            overlay=req.overlay,
        )
        return compose(spec)

    def _metadata(self, req: PostRequest, background: Background, frame) -> dict:
        return {
            "quote": req.quote,
            "author": req.author,
            "caption": req.caption,
            "background": background.id,
            "aspect_ratio": req.aspect_ratio,
            "width": frame.width,
            "height": frame.height,
        }

    def preview(self, req: ComposeRequest) -> PreviewResponse:
        background = self._assets.background(req.background)
        frame = self._compose(req, background)
        full_size = frame.size
        if frame.width > PREVIEW_MAX_WIDTH:
            frame.thumbnail((PREVIEW_MAX_WIDTH, PREVIEW_MAX_WIDTH * 4))
        buffer = BytesIO()
        frame.save(buffer, "JPEG", quality=85)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return PreviewResponse(
            image=f"data:image/jpeg;base64,{encoded}",
            width=full_size[0],
            height=full_size[1],
            background=background.id,
        )

    def post(self, req: PostRequest) -> MediaItem:
        background = self._assets.background(req.background)
        frame = self._compose(req, background)
        path = self._library.new_path(MediaKind.POST, background.name, req.aspect_ratio)
        frame.save(path, "PNG", optimize=True)
        self._library.save_metadata(path, self._metadata(req, background, frame))
        return self._library.item(MediaKind.POST, path)

    def video(self, req: VideoRequest) -> MediaItem:
        background = self._assets.background(req.background)
        frame = self._compose(req, background)
        path = self._library.new_path(MediaKind.VIDEO, background.name, req.aspect_ratio)
        encode_still_video(
            frame,
            path,
            duration=req.duration,
            fade_in=req.fade_in,
            fade_out=req.fade_out,
            fps=self._settings.video_fps,
        )
        metadata = self._metadata(req, background, frame) | {"duration": req.duration}
        self._library.save_metadata(path, metadata)
        return self._library.item(MediaKind.VIDEO, path)
