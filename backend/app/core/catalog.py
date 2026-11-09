"""Static creative catalog: themes, authors, formats and placements."""

from dataclasses import dataclass
from enum import StrEnum

THEMES: list[str] = [
    "Solitude",
    "Wisdom",
    "Discipline",
    "Consistency",
    "Focus",
    "Motivation",
    "Existence",
    "Stoicism",
    "Courage",
    "Faith",
    "Doubt",
    "Ambition",
    "Time",
    "Perseverance",
    "Inner Peace",
    "Mortality",
    "Love",
    "Suffering",
]

AUTHORS: list[str] = [
    "Marcus Aurelius",
    "Seneca",
    "Epictetus",
    "Friedrich Nietzsche",
    "Arthur Schopenhauer",
    "Fyodor Dostoevsky",
    "Franz Kafka",
    "Albert Camus",
    "Søren Kierkegaard",
    "Carl Jung",
    "Socrates",
    "Plato",
    "Aristotle",
    "Diogenes",
    "Heraclitus",
    "Epicurus",
    "Confucius",
    "Lao Tzu",
    "Sun Tzu",
    "Rumi",
    "Khalil Gibran",
    "Immanuel Kant",
    "Baruch Spinoza",
    "Niccolò Machiavelli",
    "Alan Watts",
    "African Proverb",
    "Greek Proverb",
    "Arabian Proverb",
]


class Placement(StrEnum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class MediaKind(StrEnum):
    VIDEO = "video"
    POST = "post"


@dataclass(frozen=True, slots=True)
class AspectFormat:
    key: str
    label: str
    width: int
    height: int


# Output sizes follow Instagram's recommended resolutions.
ASPECT_FORMATS: dict[str, AspectFormat] = {
    f.key: f
    for f in (
        AspectFormat("4:5", "Feed portrait", 1080, 1350),
        AspectFormat("9:16", "Reels / Story", 1080, 1920),
        AspectFormat("1:1", "Square", 1080, 1080),
        AspectFormat("16:9", "Landscape", 1920, 1080),
        AspectFormat("4:3", "Classic", 1440, 1080),
    )
}
