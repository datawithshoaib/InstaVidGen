from app.schemas.common import ApiModel
from app.schemas.media import MediaStats


class HealthResponse(ApiModel):
    status: str
    version: str


class AspectOption(ApiModel):
    key: str
    label: str
    width: int
    height: int


class FontOption(ApiModel):
    id: str
    name: str
    family: str


class BackgroundOption(ApiModel):
    id: str
    name: str
    url: str
    thumbnail_url: str


class AppConfig(ApiModel):
    version: str
    groq_configured: bool
    default_model: str
    models: list[str]
    themes: list[str]
    authors: list[str]
    aspect_ratios: list[AspectOption]
    placements: list[str]
    fonts: list[FontOption]
    backgrounds: list[BackgroundOption]
    stats: MediaStats
