"""High-level AI facade used by the API routes and batch jobs."""

import asyncio
from dataclasses import dataclass

from app.core.config import Settings
from app.core.errors import AIServiceError
from app.services.ai.llm import build_chat_model, provider_errors, resolve_model
from app.services.ai.workflow import (
    WorkflowContext,
    caption_chain,
    caption_inputs,
    content_graph,
    finalize_caption,
)


@dataclass(frozen=True, slots=True)
class GeneratedContent:
    quote: str
    caption: str | None = None
    hashtags: tuple[str, ...] = ()

    @property
    def full_caption(self) -> str | None:
        if not self.caption:
            return None
        return f"{self.caption}\n\n{' '.join(self.hashtags)}".strip()


@dataclass(frozen=True, slots=True)
class CaptionResult:
    caption: str
    hashtags: list[str]
    model: str


class ContentAI:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def model_name(self, model: str | None) -> str:
        return resolve_model(self._settings, model)

    async def generate(
        self,
        *,
        count: int,
        theme: str | None = None,
        author: str | None = None,
        avoid: list[str] | None = None,
        with_captions: bool = False,
        model: str | None = None,
        api_key: str | None = None,
    ) -> list[GeneratedContent]:
        llm = build_chat_model(self._settings, api_key=api_key, model=model)
        with provider_errors():
            state = await content_graph.ainvoke(
                {
                    "theme": theme,
                    "author": author,
                    "count": count,
                    "avoid": avoid or [],
                    "with_captions": with_captions,
                },
                context=WorkflowContext(llm=llm),
            )

        quotes: list[str] = state.get("quotes", [])
        if not quotes:
            raise AIServiceError("The model did not return a usable quote. Please try again.")
        captions = state.get("captions") or []
        return [
            GeneratedContent(
                quote=q,
                caption=captions[i].caption if i < len(captions) else None,
                hashtags=tuple(captions[i].hashtags) if i < len(captions) else (),
            )
            for i, q in enumerate(quotes)
        ]

    def generate_sync(self, **kwargs) -> list[GeneratedContent]:
        """Blocking variant for worker threads (no running event loop)."""
        return asyncio.run(self.generate(**kwargs))

    async def caption(
        self,
        *,
        quote: str,
        theme: str | None = None,
        author: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CaptionResult:
        llm = build_chat_model(self._settings, api_key=api_key, model=model)
        with provider_errors():
            draft = await caption_chain(llm).ainvoke(caption_inputs(quote, theme, author))
        draft = finalize_caption(draft)
        return CaptionResult(
            caption=draft.caption, hashtags=draft.hashtags, model=self.model_name(model)
        )
