from datetime import datetime

from app.core.catalog import MediaKind
from app.schemas.common import ApiModel


class MediaItem(ApiModel):
    kind: MediaKind
    filename: str
    url: str
    size_bytes: int
    created_at: datetime
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    quote: str | None = None
    author: str | None = None
    caption: str | None = None
    background: str | None = None
    aspect_ratio: str | None = None


class MediaStats(ApiModel):
    videos: int
    posts: int
