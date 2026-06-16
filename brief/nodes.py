import json
import re
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _parse_json_list(text: str) -> List[str]:
    """Extract a JSON list from a raw LLM response.

    The LLM is asked to return a JSON array, but sometimes it adds extra
    wording. This function tries ``json.loads`` first and falls back to a
    simple line‑splitting heuristic.
    """
    try:
        return json.loads(text)
    except Exception:
        # Remove any surrounding markdown or text and split on newlines
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        cleaned = []
        for ln in lines:
            # Strip leading bullets or numbers
            ln = re.sub(r"^[\-\*\d\.\s]+", "", ln)
            cleaned.append(ln)
        return cleaned

# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def outline(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a 4‑5 item outline for the supplied ``topic``.

    The node returns a new state containing ``outline``, resets ``step_index``
    to ``0`` and creates an empty ``notes`` list.
    """
    topic = state["topic"]
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    prompt = (
        f"You are an assistant that creates a short research outline.\n"
        f"Given the topic: \"{topic}\", produce a JSON array (list) containing 4 to 5 concise research points. "
        "Each point should be a short sentence without numbering."
    )
    response = llm.invoke(prompt)
    outline_list = _parse_json_list(response.content)
    # Ensure we have 4‑5 items – truncate or pad if necessary
    if len(outline_list) > 5:
        outline_list = outline_list[:5]
    elif len(outline_list) < 4:
        # If the model returned too few, just keep what we have; the loop will handle it.
        pass
    return {"outline": outline_list, "step_index": 0, "notes": []}


def research_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """Perform a single Tavily search for the current outline point and summarise it.

    The function:
    1. Retrieves the current point using ``step_index``.
    2. Calls Tavily (max 5 results) to obtain raw web snippets.
    3. Summarises the snippets with the LLM into a 5‑8 sentence note.
    4. Appends the note to ``notes`` and increments ``step_index``.
    """
    outline: List[str] = state["outline"]  # type: ignore
    idx: int = state["step_index"]
    point = outline[idx]

    # ---------------------------------------------------------------
    # 1️⃣ Web search via Tavily
    # ---------------------------------------------------------------
    search_tool = TavilySearchResults(max_results=5)
    raw_results = search_tool.run(point)

    # ---------------------------------------------------------------
    # 2️⃣ Summarise with LLM
    # ---------------------------------------------------------------
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    summarise_prompt = (
        f"Summarise the following web‑search results about the topic below into a concise note consisting of 5‑8 sentences. "
        f"Use only factual information present in the results.\n\n"
        f"Topic: {point}\n\nResults:\n{raw_results}"
    )
    summary = llm.invoke(summarise_prompt).content

    # ---------------------------------------------------------------
    # 3️⃣ Update state
    # ---------------------------------------------------------------
    notes = list(state.get("notes", []))
    notes.append(summary)
    return {"notes": notes, "step_index": idx + 1}


def synthesize(state: Dict[str, Any]) -> Dict[str, Any]:
    """Combine all collected notes into a coherent brief.

    The LLM receives the notes together with the original outline titles so it
    can create headings and smooth transitions.
    """
    topic = state["topic"]
    outline: List[str] = state["outline"]  # type: ignore
    notes: List[str] = state["notes"]

    # Build a structured representation for the LLM – headings + notes
    sections = []
    for title, note in zip(outline, notes):
        sections.append(f"## {title}\n{note}\n")
    sections_text = "\n".join(sections)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    prompt = (
        f"You are an expert writer. Using the sections below, produce a cohesive research brief (about half to one page) for the topic \"{topic}\". "
        "The brief should have a brief introduction, the provided sections with smooth transitions, and a concise conclusion.\n\n"
        f"Sections:\n{sections_text}"
    )
    brief = llm.invoke(prompt).content
    return {"final_brief": brief}
