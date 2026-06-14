from __future__ import annotations

from typing import List, TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint import InMemorySaver
from langgraph.types import interrupt, Command

from llm_utils import generate_scene, generate_ending


class StoryState(TypedDict, total=False):
    """State stored in the LangGraph checkpoint.

    Fields are optional because they are filled progressively during execution.
    """

    theme: str
    hook: Optional[str]
    options: Optional[List[str]]
    user_choice: Optional[str]
    ending: Optional[str]


def story_node(state: dict, config: dict, input: dict | None = None) -> dict:
    """A single node that handles both phases of the adventure.

    * First call (no ``input``) – generates the hook and options, stores them in ``state``
      and returns an ``interrupt`` payload.
    * Resumed call (``input`` contains the payload with the user's answer) – stores the
      answer, generates the ending and returns the updated ``state``.
    """
    # Phase 1 – we have not yet generated a hook.
    if not state.get("hook"):
        theme = state.get("theme", "An adventure")
        hook, options = generate_scene(theme)
        state["hook"] = hook
        state["options"] = options
        payload = {
            "type": "choice",
            "question": f"{hook}\nWhat do we do?",
            "options": options,
        }
        return interrupt(payload)

    # Phase 2 – we have been resumed after the interrupt.
    if input is None:
        # Defensive: if for some reason we are called without a payload, just return state.
        return state
    answer = input.get("answer")
    state["user_choice"] = answer
    ending = generate_ending(state["hook"], answer)
    state["ending"] = ending
    return state


# Build the graph.
graph = StateGraph(StoryState)
graph.add_node("story", story_node)
graph.add_edge(START, "story")
graph.add_edge("story", END)
# Compile with an in‑memory checkpoint saver so that ``resume`` works.
graph = graph.compile(checkpointer=InMemorySaver())
