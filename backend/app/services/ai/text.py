"""Pure text helpers for cleaning LLM output."""

import re

_WRAPPING_QUOTES = "\"'“”‘’«»„"
# "... — Marcus Aurelius" / "... - Seneca": 1-4 capitalised words after a dash.
_TRAILING_ATTRIBUTION = re.compile(r"\s+[—–―-]{1,2}\s*(?:[A-Z][\w.'’]*\s?){1,4}$")
_LIST_PREFIX = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s+")
_NON_WORD = re.compile(r"[^a-z0-9]+")

MIN_QUOTE_CHARS = 8
MAX_QUOTE_CHARS = 280


def clean_quote(text: str) -> str:
    """Strip list markers, wrapping quotation marks, attributions and extra whitespace."""
    text = " ".join(text.split())
    text = _LIST_PREFIX.sub("", text)
    text = _TRAILING_ATTRIBUTION.sub("", text)
    while len(text) > 1 and text[0] in _WRAPPING_QUOTES and text[-1] in _WRAPPING_QUOTES:
        text = text[1:-1].strip()
    return text.strip()


def is_acceptable_quote(text: str) -> bool:
    return MIN_QUOTE_CHARS <= len(text) <= MAX_QUOTE_CHARS


def quote_fingerprint(text: str) -> str:
    """Normalised key used for de-duplication."""
    return _NON_WORD.sub(" ", text.lower()).strip()


def normalize_hashtags(tags: list[str], limit: int = 10) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in tags:
        for token in raw.replace(",", " ").split():
            word = re.sub(r"[^\w]", "", token.lstrip("#"))
            if not word or word.lower() in seen:
                continue
            seen.add(word.lower())
            result.append(f"#{word}")
    return result[:limit]
