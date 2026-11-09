"""Wires services together once per application instance."""

from dataclasses import dataclass

from app.core.config import Settings
from app.services.ai.service import ContentAI
from app.services.batch import BatchManager
from app.services.media.assets import AssetLibrary
from app.services.media.library import MediaLibrary
from app.services.media.renderer import RenderService


@dataclass(frozen=True, slots=True)
class Services:
    settings: Settings
    ai: ContentAI
    assets: AssetLibrary
    library: MediaLibrary
    renderer: RenderService
    batches: BatchManager

    @classmethod
    def create(cls, settings: Settings) -> "Services":
        settings.ensure_directories()
        ai = ContentAI(settings)
        assets = AssetLibrary(settings)
        library = MediaLibrary(settings)
        renderer = RenderService(settings, assets, library)
        batches = BatchManager(settings, ai, renderer, assets)
        return cls(settings, ai, assets, library, renderer, batches)
