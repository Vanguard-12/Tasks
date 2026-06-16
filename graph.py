from typing import Dict, Any, List
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint import InMemorySaver
from langgraph.types import interrupt, Command
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from state import AdventureState

# Initialise a single LLM instance – you can change the model name if you wish.
_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)


def _parse_scene_response(text: str) -> Dict[str, Any]:
    """Parse the LLM response that contains a hook and three options.

    Expected format (exactly as prompted)::

        Hook: <hook text>
        Options:
        1) <option 1>
        2) <option 2>
        3) <option 3>

    The function is tolerant to extra whitespace.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    hook = ""
    options: List[str] = []
    mode = None
    for line in lines:
        if line.lower().startswith("hook:"):
            hook = line.split(":", 1)[1].strip()
            mode = None
        elif line.lower().startswith("options"):
            mode = "options"
        elif mode == "options" and line[0].isdigit():
            # line like "1) go left"
            parts = line.split(")", 1)
            if len(parts) == 2:
                opt = parts[1].strip()
                options.append(opt)
    # Fallback – if we didn't detect the explicit markers, try a simple split.
    if not hook or len(options) != 3:
        # Very naive fallback: first line is hook, next three lines are options.
        if lines:
            hook = lines[0]
        options = lines[1:4]
    return {"hook": hook, "options": options}


def adventure_node(state: AdventureState) -> Any:
    """Single node that handles both phases of the adventure.

    * If ``user_choice`` is not yet present, it generates the hook + options
      and raises an ``interrupt``.
    * If ``user_choice`` is present, it generates the ending and returns the
      updated state.
    """
    # Phase 1 – generate hook and options.
    if "user_choice" not in state:
        theme = state.get("theme", "An unexpected adventure")
        prompt = (
            f"Theme: {theme}\n"
            "Write a short story hook (2‑3 sentences) and exactly three possible actions the hero can take.\n"
            "Return the result in the following format:\n"
            "Hook: <hook text>\n"
            "Options:\n"
            "1) <option 1>\n"
            "2) <option 2>\n"
            "3) <option 3>"
        )
        response = _llm.invoke([HumanMessage(content=prompt)])
        parsed = _parse_scene_response(response.content)
        state["hook"] = parsed["hook"]
        state["options"] = parsed["options"]
        # Payload for the interrupt – the runner will present this to the user.
        payload = {
            "type": "choice",
            "question": parsed["hook"],
            "options": parsed["options"],
        }
        return interrupt(payload)

    # Phase 2 – we have a user choice, generate the ending.
    hook = state.get("hook", "")
    choice = state.get("user_choice", "")
    prompt = (
        f"Hook: {hook}\n"
        f"User chose: {choice}\n"
        "Write a short ending (2‑3 sentences) that follows naturally from this choice."
    )
    response = _llm.invoke([HumanMessage(content=prompt)])
    state["ending"] = response.content.strip()
    return state


def build_graph() -> Any:
    """Construct and compile the LangGraph for the adventure game.

    Returns the compiled graph ready to be streamed.
    """
    graph = StateGraph(AdventureState)
    graph.add_node("adventure", adventure_node)
    graph.add_edge(START, "adventure")
    graph.add_edge("adventure", END)
    compiled = graph.compile(checkpointer=InMemorySaver())
    return compiled
