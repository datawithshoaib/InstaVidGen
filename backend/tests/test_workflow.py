"""Exercise the LangGraph workflow with a fake chat model (no network)."""

import asyncio
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from app.services.ai.prompts import CaptionDraft, QuoteDrafts
from app.services.ai.workflow import WorkflowContext, content_graph


class ScriptedModel(GenericFakeChatModel):
    """Returns queued structured outputs for `with_structured_output` calls."""

    outputs: dict[Any, list[Any]]

    def with_structured_output(self, schema, **kwargs):  # type: ignore[override]
        queue = self.outputs[schema]
        return RunnableLambda(lambda _: queue.pop(0) if len(queue) > 1 else queue[0])


def run(llm, **state):
    return asyncio.run(content_graph.ainvoke(state, context=WorkflowContext(llm=llm)))


def make_llm(quote_rounds, caption=None):
    return ScriptedModel(
        messages=iter([AIMessage(content="")]),
        outputs={
            QuoteDrafts: [QuoteDrafts(quotes=q) for q in quote_rounds],
            CaptionDraft: [caption or CaptionDraft(caption="c", hashtags=["a"])],
        },
    )


def test_workflow_dedupes_and_retries_until_count_reached():
    llm = make_llm([["“Same line here.”", "same line here", "x"], ["A second idea entirely."]])
    state = run(llm, count=2, avoid=[], with_captions=False)
    assert state["quotes"] == ["Same line here.", "A second idea entirely."]
    assert state["rounds"] == 2


def test_workflow_respects_avoid_list_and_writes_captions():
    llm = make_llm(
        [["Old quote we used.", "Fresh quote for today."]],
        caption=CaptionDraft(caption=" Deep. ", hashtags=["stoic", "#Stoic", "#mind"]),
    )
    state = run(llm, count=1, avoid=["Old quote we used."], with_captions=True)
    assert state["quotes"] == ["Fresh quote for today."]
    assert state["captions"][0].caption == "Deep."
    assert state["captions"][0].hashtags == ["#stoic", "#mind"]


def test_workflow_gives_up_after_max_rounds():
    llm = make_llm([["dup line one"]])
    state = run(llm, count=3, avoid=[], with_captions=False)
    assert state["quotes"] == ["dup line one"]
    assert state["rounds"] == 3
