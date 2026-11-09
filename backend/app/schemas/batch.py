from datetime import datetime
from typing import Literal, Self

from pydantic import Field, model_validator

from app.core.catalog import MediaKind
from app.schemas.common import ApiModel
from app.schemas.media import MediaItem
from app.schemas.render import StyleSettings, VideoTiming

BatchStatus = Literal["queued", "running", "completed", "failed"]


class BatchRequest(StyleSettings, VideoTiming):
    kind: MediaKind = MediaKind.VIDEO
    count: int = Field(default=5, ge=1, le=20)
    quote_source: Literal["ai", "manual"] = "ai"
    quote: str | None = Field(default=None, max_length=600)
    theme: str | None = Field(default=None, max_length=60)
    author: str | None = Field(default=None, max_length=80)
    show_author: bool = True
    with_captions: bool = True
    model: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def _manual_needs_quote(self) -> Self:
        if self.quote_source == "manual" and not self.quote:
            raise ValueError("A quote is required when quoteSource is 'manual'.")
        return self


class BatchJob(ApiModel):
    id: str
    status: BatchStatus
    kind: MediaKind
    total: int
    completed: int = 0
    stage: str = "Queued"
    items: list[MediaItem] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    created_at: datetime
    finished_at: datetime | None = None
