"""Compose a quote over a background image with Pillow."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.core.catalog import AspectFormat, Placement

TEXT_COLOR = (255, 255, 255, 255)
ATTRIBUTION_COLOR = (236, 226, 208, 255)
SHADOW_COLOR = (0, 0, 0, 210)

MAX_TEXT_WIDTH = 0.82  # fraction of image width
MAX_TEXT_HEIGHT = 0.62  # fraction of image height
MIN_FONT_FRACTION = 0.018  # smallest font when auto-shrinking, fraction of height


@dataclass(frozen=True, slots=True)
class ComposeSpec:
    background: Path
    quote: str
    aspect: AspectFormat
    font: Path | None
    attribution_font: Path | None
    author: str | None = None
    font_scale: float = 4.5
    placement: Placement = Placement.CENTER
    overlay: int = 35


@lru_cache(maxsize=24)
def _cover(path: Path, width: int, height: int, mtime: float) -> Image.Image:
    """Load a background, center-crop to the target ratio and resize (cached)."""
    with Image.open(path) as src:
        img = src.convert("RGB")
    target_ratio = width / height
    w, h = img.size
    if w / h > target_ratio:
        new_w = round(h * target_ratio)
        box = ((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h)
    else:
        new_h = round(w / target_ratio)
        box = (0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h)
    return img.resize((width, height), Image.Resampling.LANCZOS, box=box)


@lru_cache(maxsize=128)
def _font(path: Path | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path is not None:
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def _wrap(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Greedy word wrap that keeps the user's explicit line breaks."""
    lines: list[str] = []
    for paragraph in text.splitlines() or [text]:
        words = paragraph.split()
        if not words:
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if draw.textlength(candidate, font=font) <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def _fit_text(spec: ComposeSpec, width: int, height: int, draw: ImageDraw.ImageDraw):
    """Pick the largest font size (up to the requested one) that fits the text box."""
    max_w = int(width * MAX_TEXT_WIDTH)
    max_h = int(height * MAX_TEXT_HEIGHT)
    size = max(12, int(height * spec.font_scale / 100))
    min_size = max(12, int(height * MIN_FONT_FRACTION))
    while True:
        font = _font(spec.font, size)
        spacing = int(size * 0.32)
        text = "\n".join(_wrap(spec.quote, font, max_w, draw))
        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
        if (box[3] - box[1] <= max_h and box[2] - box[0] <= max_w) or size <= min_size:
            return font, size, spacing, text, box
        size = max(min_size, int(size * 0.92))


def compose(spec: ComposeSpec) -> Image.Image:
    width, height = spec.aspect.width, spec.aspect.height
    base = _cover(spec.background, width, height, spec.background.stat().st_mtime).copy()

    if spec.overlay > 0:
        shade = Image.new("RGB", base.size, (0, 0, 0))
        base = Image.blend(base, shade, spec.overlay / 100)

    measure = ImageDraw.Draw(base)
    font, size, spacing, text, box = _fit_text(spec, width, height, measure)
    text_w, text_h = box[2] - box[0], box[3] - box[1]

    attribution = f"— {spec.author.strip()}" if spec.author and spec.author.strip() else None
    attr_font = _font(spec.attribution_font or spec.font, max(12, int(size * 0.58)))
    attr_gap = int(size * 0.9)
    attr_h = 0
    if attribution:
        attr_box = measure.textbbox((0, 0), attribution, font=attr_font)
        attr_h = attr_gap + (attr_box[3] - attr_box[1])

    block_h = text_h + attr_h
    match spec.placement:
        case Placement.TOP:
            top = int(height * 0.12)
        case Placement.BOTTOM:
            top = height - block_h - int(height * 0.14)
        case _:
            top = (height - block_h) // 2

    # Draw shadow and text on separate layers so the shadow can be blurred softly.
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw, text_draw = ImageDraw.Draw(shadow), ImageDraw.Draw(layer)
    offset = max(2, size // 22)

    text_xy = ((width - text_w) / 2 - box[0], top - box[1])
    kwargs = {"font": font, "spacing": spacing, "align": "center"}
    shadow_draw.multiline_text((text_xy[0], text_xy[1] + offset), text, fill=SHADOW_COLOR, **kwargs)
    text_draw.multiline_text(text_xy, text, fill=TEXT_COLOR, **kwargs)

    if attribution:
        a_box = measure.textbbox((0, 0), attribution, font=attr_font)
        a_xy = ((width - (a_box[2] - a_box[0])) / 2 - a_box[0], top + text_h + attr_gap - a_box[1])
        shadow_xy = (a_xy[0], a_xy[1] + offset)
        shadow_draw.text(shadow_xy, attribution, font=attr_font, fill=SHADOW_COLOR)
        text_draw.text(a_xy, attribution, font=attr_font, fill=ATTRIBUTION_COLOR)

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(3, size // 8)))
    result = base.convert("RGBA")
    result.alpha_composite(shadow)
    result.alpha_composite(layer)
    return result.convert("RGB")
