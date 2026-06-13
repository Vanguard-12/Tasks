import os
import json
import argparse
from typing import TypedDict, List, Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables (TAVILY_API_KEY, OPENAI_API_KEY)
load_dotenv()

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------
class BriefState(TypedDict):
    topic: str
    outline: Optional[List[str]]
    step_index: int
    notes: List[str]
    final_brief: Optional[str]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _ensure_api_keys():
    missing = []
    if not os.getenv("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please add them to a .env file or your environment."
        )

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------
def outline_node(state: BriefState):
    """Generate a 4‑5 item outline for the given topic using an LLM."""
    _ensure_api_keys()
    topic = state["topic"]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an assistant that creates concise research outlines."),
            (
                "human",
                "Provide a JSON array (list) of 4‑5 short research points for the topic: {topic}. "
                "Each point should be a single sentence. Return ONLY the JSON array.",
            ),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | llm
    result = chain.invoke({"topic": topic})
    try:
        outline = json.loads(result.content.strip())
    except Exception:
        # Fallback: split lines and strip bullets
        outline = [
            line.strip("- ").strip()
            for line in result.content.splitlines()
            if line.strip()
        ]
    # Ensure we have at most 5 items
    outline = outline[:5]
    return {"outline": outline, "step_index": 0, "notes": []}


def research_step_node(state: BriefState):
    """Research a single outline point via Tavily and summarise it."""
    _ensure_api_keys()
    outline = state.get("outline") or []
    idx = state.get("step_index", 0)
    if idx >= len(outline):
        return {}
    point = outline[idx]
    # Perform a single Tavily search
    search_tool = TavilySearchResults()
    try:
        search_result = search_tool.run(point)
    except Exception as e:
        raise RuntimeError(f"Tavily search failed for point '{point}': {e}")
    # Summarise the result with the LLM
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an assistant that writes a concise research note (5‑8 sentences) based on a web‑search result.",
            ),
            (
                "human",
                "Using the following search result, write a short note about the point: {point}. "
                "Include any useful URLs. Keep the note factual and concise.\n\nSearch result:\n{search_result}",
            ),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | llm
    note = chain.invoke({"point": point, "search_result": search_result}).content
    notes = state.get("notes", []).copy()
    notes.append(note)
    return {"notes": notes, "step_index": idx + 1}


def synthesize_node(state: BriefState):
    """Combine all notes into a coherent brief with headings."""
    _ensure_api_keys()
    outline = state.get("outline") or []
    notes = state.get("notes") or []
    # Build a combined string with headings for the LLM
    combined = "\n\n".join(
        [f"## {outline[i]}\n{notes[i]}" for i in range(min(len(outline), len(notes)))]
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an assistant that creates a short research brief (½‑1 page) from given notes. "
                "Preserve the headings, ensure logical flow, and avoid repetition.",
            ),
            ("human", "Combine the following sections into a single brief:\n\n{combined}"),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | llm
    final = chain.invoke({"combined": combined}).content
    return {"final_brief": final}

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(BriefState)
    graph.add_node("outline", outline_node)
    graph.add_node("research_step", research_step_node)
    graph.add_node("synthesize", synthesize_node)
    graph.set_entry_point("outline")
    graph.add_edge("outline", "research_step")
    # Conditional edge: continue researching until all outline items are processed
    graph.add_conditional_edges(
        "research_step",
        lambda s: "synthesize" if s["step_index"] >= len(s["outline"]) else "research_step",
    )
    graph.add_edge("synthesize", END)
    return graph.compile()

# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LangGraph research brief demo")
    parser.add_argument(
        "--topic",
        type=str,
        default="Как студенту безопасно подключать MCP к LangChain",
        help="Research topic",
    )
    args = parser.parse_args()
    try:
        graph = build_graph()
        result = graph.invoke({"topic": args.topic})
    except EnvironmentError as ee:
        print(f"[Error] {ee}")
        return
    except Exception as exc:
        print(f"[Unexpected error] {exc}")
        return

    # Print outline
    outline = result.get("outline", [])
    print("\n=== Outline ===")
    for i, item in enumerate(outline, 1):
        print(f"{i}. {item}")

    # Print each step note
    notes = result.get("notes", [])
    print("\n=== Research Steps ===")
    for i, note in enumerate(notes, 1):
        print(f"[Step {i}]\n{note}\n")

    # Print final brief
    final = result.get("final_brief", "")
    print("\n=== Final Brief ===\n")
    print(final)

if __name__ == "__main__":
    main()
