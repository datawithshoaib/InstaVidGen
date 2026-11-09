"""LangGraph content workflow.

    START -> draft_quotes -> review_quotes --(short & retries left)--> draft_quotes
                                         \\--(captions requested)--> write_captions -> END
                                          \\-------------------------------------------> END

`review_quotes` cleans and de-duplicates candidates, so asking for N quotes reliably
returns N distinct, usable quotes (or as many as the model could produce in
MAX_DRAFT_ROUNDS rounds).
"""

from dataclasses import dataclass
from typing import TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from app.services.ai.prompts import (
    CaptionDraft,
    QuoteDrafts,
    avoid_block,
    caption_context,
    caption_prompt,
    quote_brief,
    quote_prompt,
)
from app.services.ai.text import (
    clean_quote,
    is_acceptable_quote,
    normalize_hashtags,
    quote_fingerprint,
)

MAX_DRAFT_ROUNDS = 3
CAPTION_CONCURRENCY = 4


@dataclass(frozen=True, slots=True)
class WorkflowContext:
    llm: BaseChatModel


class ContentState(TypedDict, total=False):
    # inputs
    theme: str | None
    author: str | None
    count: int
    avoid: list[str]
    with_captions: bool
    # working state
    drafts: list[str]
    rounds: int
    # outputs
    quotes: list[str]
    captions: list[CaptionDraft]


def caption_chain(llm: BaseChatModel) -> Runnable:
    return caption_prompt | llm.with_structured_output(CaptionDraft)


def caption_inputs(quote: str, theme: str | None, author: str | None) -> dict:
    return {"quote": quote, "context": caption_context(theme, author)}


def finalize_caption(draft: CaptionDraft) -> CaptionDraft:
    return CaptionDraft(caption=draft.caption.strip(), hashtags=normalize_hashtags(draft.hashtags))


# ------------------------------------------------------------------ nodes


async def draft_quotes(state: ContentState, runtime: Runtime[WorkflowContext]) -> dict:
    accepted = state.get("quotes", [])
    missing = state["count"] - len(accepted)
    # Ask for a couple of extras so review can discard weak or duplicate lines.
    requested = missing + min(2, missing)
    chain = quote_prompt | runtime.context.llm.with_structured_output(QuoteDrafts)
    result: QuoteDrafts = await chain.ainvoke(
        {
            "count": requested,
            "brief": quote_brief(state.get("theme"), state.get("author")),
            "avoid_block": avoid_block([*state.get("avoid", []), *accepted]),
        }
    )
    return {"drafts": result.quotes, "rounds": state.get("rounds", 0) + 1}


def review_quotes(state: ContentState) -> dict:
    accepted = list(state.get("quotes", []))
    seen = {quote_fingerprint(q) for q in [*state.get("avoid", []), *accepted]}
    for raw in state.get("drafts", []):
        if len(accepted) >= state["count"]:
            break
        quote = clean_quote(raw)
        key = quote_fingerprint(quote)
        if is_acceptable_quote(quote) and key not in seen:
            seen.add(key)
            accepted.append(quote)
    return {"quotes": accepted, "drafts": []}


async def write_captions(state: ContentState, runtime: Runtime[WorkflowContext]) -> dict:
    chain = caption_chain(runtime.context.llm)
    drafts: list[CaptionDraft] = await chain.abatch(
        [caption_inputs(q, state.get("theme"), state.get("author")) for q in state["quotes"]],
        config={"max_concurrency": CAPTION_CONCURRENCY},
    )
    return {"captions": [finalize_caption(d) for d in drafts]}


def route_after_review(state: ContentState) -> str:
    if len(state["quotes"]) < state["count"] and state["rounds"] < MAX_DRAFT_ROUNDS:
        return "draft_quotes"
    if state.get("with_captions") and state["quotes"]:
        return "write_captions"
    return END


def build_content_graph():
    graph = StateGraph(ContentState, context_schema=WorkflowContext)
    graph.add_node("draft_quotes", draft_quotes)
    graph.add_node("review_quotes", review_quotes)
    graph.add_node("write_captions", write_captions)

    graph.add_edge(START, "draft_quotes")
    graph.add_edge("draft_quotes", "review_quotes")
    graph.add_conditional_edges(
        "review_quotes", route_after_review, ["draft_quotes", "write_captions", END]
    )
    graph.add_edge("write_captions", END)
    return graph.compile(name="content_workflow")


content_graph = build_content_graph()
