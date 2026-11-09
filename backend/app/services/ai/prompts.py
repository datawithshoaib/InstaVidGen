"""Prompt templates and structured-output schemas for the content workflow."""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# ---------------------------------------------------------------- schemas


class QuoteDrafts(BaseModel):
    """A set of quote candidates."""

    quotes: list[str] = Field(
        description=(
            "The quotes. Each item is only the quote text: no author, no numbering, "
            "no surrounding quotation marks."
        )
    )


class CaptionDraft(BaseModel):
    """An Instagram caption for a quote post."""

    caption: str = Field(
        description="2-4 short lines unpacking the idea behind the quote. No hashtags here."
    )
    hashtags: list[str] = Field(description="6-10 relevant Instagram hashtags, each with a #.")


# ---------------------------------------------------------------- prompts

QUOTE_SYSTEM = """You curate philosophical quotes for an Instagram page with a serious, \
contemplative voice.

Rules:
- Every quote is striking, compact (ideally under 25 words) and reads well on an image.
- No clichés, greeting-card lines, hustle-culture slogans or emojis.
- Clear modern English.
- Each quote in the set must express a clearly different idea."""

QUOTE_HUMAN = """Write {count} quote(s).

{brief}

{avoid_block}"""

AUTHOR_BRIEF = """Source: {author}.
Use genuine passages from {author}'s own works, letters or recorded sayings, \
preferring lesser-known lines over the most circulated ones. Translations may be \
lightly modernised. Do not invent lines and attribute them to {author}; if you are \
unsure of a passage, choose another one you are sure of.{theme_hint}"""

THEME_BRIEF = """Theme: {theme}.
Write original aphorisms on this theme that feel timeless and leave the reader \
thinking."""

OPEN_BRIEF = """Any theme. Write original aphorisms that feel timeless, challenge an \
assumption and leave the reader thinking."""

quote_prompt = ChatPromptTemplate.from_messages([("system", QUOTE_SYSTEM), ("human", QUOTE_HUMAN)])

CAPTION_SYSTEM = """You write Instagram captions for a page sharing philosophical quotes.
Voice: thoughtful, direct, never salesy. No emojis, no "Double tap", no "Follow for more"."""

CAPTION_HUMAN = """Quote: "{quote}"
{context}
Write the caption and hashtags."""

caption_prompt = ChatPromptTemplate.from_messages(
    [("system", CAPTION_SYSTEM), ("human", CAPTION_HUMAN)]
)


def quote_brief(theme: str | None, author: str | None) -> str:
    if author:
        theme_hint = f" Prefer passages about {theme.lower()}." if theme else ""
        return AUTHOR_BRIEF.format(author=author, theme_hint=theme_hint)
    if theme:
        return THEME_BRIEF.format(theme=theme.lower())
    return OPEN_BRIEF


def avoid_block(avoid: list[str]) -> str:
    if not avoid:
        return ""
    lines = "\n".join(f"- {q}" for q in avoid[-30:])
    return f"Do not repeat or paraphrase any of these:\n{lines}"


def caption_context(theme: str | None, author: str | None) -> str:
    parts = []
    if author:
        parts.append(f"Attributed to: {author}")
    if theme:
        parts.append(f"Theme: {theme}")
    return "\n".join(parts)
