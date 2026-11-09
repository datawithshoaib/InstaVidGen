from typing import Literal, Self

from pydantic import Field, model_validator

from app.core.catalog import Placement
from app.schemas.common import ApiModel

AspectRatio = Literal["4:5", "9:16", "1:1", "16:9", "4:3"]


class StyleSettings(ApiModel):
    aspect_ratio: AspectRatio = "4:5"
    font_id: str = Field(default="default", max_length=120)
    font_scale: float = Field(default=4.5, ge=2.0, le=10.0, description="Font size, % of height.")
    placement: Placement = Placement.CENTER
    overlay: int = Field(default=35, ge=0, le=85, description="Background darkening, %.")


class VideoTiming(ApiModel):
    duration: float = Field(default=6.0, ge=2.0, le=30.0)
    fade_in: float = Field(default=1.5, ge=0.0, le=5.0)
    fade_out: float = Field(default=0.5, ge=0.0, le=5.0)

    @model_validator(mode="after")
    def _fades_fit(self) -> Self:
        if self.fade_in + self.fade_out > self.duration:
            raise ValueError("Fade-in plus fade-out cannot exceed the video duration.")
        return self


class ComposeRequest(StyleSettings):
    quote: str = Field(min_length=1, max_length=600)
    author: str | None = Field(default=None, max_length=80, description="Attribution line.")
    background: str | None = Field(default=None, description="Background id; random if empty.")


class PostRequest(ComposeRequest):
    caption: str | None = Field(default=None, max_length=3000)


class VideoRequest(PostRequest, VideoTiming):
    pass


class PreviewResponse(ApiModel):
    image: str = Field(description="JPEG data URI.")
    width: int
    height: int
    background: str
