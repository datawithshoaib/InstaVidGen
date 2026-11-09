"""Background images and fonts shipped in `backend/assets`."""

import random
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from app.core.config import Settings
from app.core.errors import NotFoundError

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
FONT_SUFFIXES = {".ttf", ".otf"}

DEFAULT_FONT_ID = "Montserrat/Montserrat-ExtraBold.ttf"
ATTRIBUTION_FONT_ID = "Cinzel/Cinzel-Bold.ttf"
THUMBNAIL_WIDTH = 360

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z])(?=[A-Z])")


@dataclass(frozen=True, slots=True)
class Font:
    id: str
    name: str
    family: str
    path: Path


@dataclass(frozen=True, slots=True)
class Background:
    id: str
    name: str
    path: Path


def safe_child(directory: Path, relative: str) -> Path:
    """Resolve `relative` inside `directory`, rejecting path traversal."""
    base = directory.resolve()
    candidate = (base / relative).resolve()
    if not candidate.is_relative_to(base) or candidate == base:
        raise NotFoundError("File not found.")
    return candidate


def _background_name(path: Path) -> str:
    return path.stem.replace("_s ", "'s ")


def _font_display_name(path: Path) -> str:
    # "Montserrat-ExtraBoldItalic" -> "Montserrat Extra Bold Italic"
    family, _, style = path.stem.partition("-")
    style = _CAMEL_BOUNDARY.sub(" ", style) if style else "Regular"
    return f"{family} {style}"


class AssetLibrary:
    def __init__(self, settings: Settings) -> None:
        self._backgrounds_dir = settings.backgrounds_dir
        self._fonts_dir = settings.fonts_dir
        self._thumbnails_dir = settings.thumbnails_dir

    # ------------------------------------------------------------ backgrounds

    def backgrounds(self) -> list[Background]:
        if not self._backgrounds_dir.is_dir():
            return []
        return [
            Background(id=p.name, name=_background_name(p), path=p)
            for p in sorted(self._backgrounds_dir.iterdir(), key=lambda p: p.name.lower())
            if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
        ]

    def background(self, background_id: str | None) -> Background:
        """Return the requested background, or a random one when none is given."""
        if background_id:
            path = safe_child(self._backgrounds_dir, background_id)
            if not path.is_file():
                raise NotFoundError(f"Background '{background_id}' not found.")
            return Background(id=path.name, name=_background_name(path), path=path)
        choices = self.backgrounds()
        if not choices:
            raise NotFoundError("No background images found in backend/assets/backgrounds.")
        return random.choice(choices)

    def thumbnail(self, background_id: str) -> Path:
        """Small cached JPEG for the picker grid (source PNGs are several MB each)."""
        source = self.background(background_id).path
        target = self._thumbnails_dir / f"{source.stem}.jpg"
        if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
            self._thumbnails_dir.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as img:
                img = img.convert("RGB")
                img.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_WIDTH * 2))
                img.save(target, "JPEG", quality=82, optimize=True)
        return target

    # ------------------------------------------------------------------ fonts

    def fonts(self) -> list[Font]:
        if not self._fonts_dir.is_dir():
            return []
        fonts = [
            Font(
                id=p.relative_to(self._fonts_dir).as_posix(),
                name=_font_display_name(p),
                family=p.parent.name if p.parent != self._fonts_dir else p.stem.split("-")[0],
                path=p,
            )
            for p in self._fonts_dir.rglob("*")
            if p.suffix.lower() in FONT_SUFFIXES
        ]
        return sorted(fonts, key=lambda f: (f.family, f.name))

    def font_path(self, font_id: str | None) -> Path | None:
        """Resolve a font id; unknown ids fall back to the default font."""
        for candidate in (font_id, DEFAULT_FONT_ID):
            if not candidate or candidate == "default":
                continue
            try:
                path = safe_child(self._fonts_dir, candidate)
            except NotFoundError:
                continue
            if path.is_file():
                return path
        return None

    def attribution_font_path(self) -> Path | None:
        return self.font_path(ATTRIBUTION_FONT_ID)
