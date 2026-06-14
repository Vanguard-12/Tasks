import os
import sys
from typing import TypedDict, List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Replace with Ollama if desired
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemoryCheckpoint
from tavily import TavilyClient

# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise EnvironmentError("TAVILY_API_KEY not found in environment variables")

# ------------------------------------------------------------
# LLM configuration – OpenAI by default
# ------------------------------------------------------------
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# ------------------------------------------------------------
# State definition
# ------------------------------------------------------------
class BriefState(TypedDict):
    topic: str
    outline: Optional[List[str]]
    step_index: int
    notes: List[str]
    final_brief: Optional[str]

# ------------------------------------------------------------
# Prompt templates
# ------------------------------------------------------------
OUTLINE_PROMPT = PromptTemplate.from_template(
    "You are an academic researcher. Create a concise outline (4‑5 bullet points) for a short research brief on the following topic.\n\nTopic: {topic}\n\nReturn the outline as a numbered list without extra commentary."
)

NOTE_PROMPT = PromptTemplate.from_template(
    "You have just performed a web search for the following query and obtained the results below (titles and snippets). Summarise the most relevant information in 5‑8 sentences, suitable for a student research brief. Include at least one URL if possible.\n\nQuery: {query}\n\nSearch results:\n{search_results}\n"
)

SYNTHESIZE_PROMPT = PromptTemplate.from_template(
    "You have collected the following notes for a research brief. Combine them into a coherent ½‑1 page text. Use the original outline items as headings (e.g., **1. …**). Ensure the final text flows naturally and does not simply concatenate the notes.\n\nOutline:\n{outline}\n\nNotes:\n{notes}\n"
)

# ------------------------------------------------------------
# Helper: Tavily search (single call)
# ------------------------------------------------------------
client = TavilyClient(api_key=TAVILY_API_KEY)

def tavily_search(query: str) -> str:
    """Perform a single Tavily search and return a formatted string of titles + snippets."""
    try:
        resp = client.search(query=query, search_depth=2, max_results=5)
        results = resp.get("results", [])
        if not results:
            return "No results found."
        formatted = []
        for r in results:
            title = r.get("title", "")
            snippet = r.get("content", "")
            url = r.get("url", "")
            formatted.append(f"- {title}\n  {snippet}\n  {url}")
        return "\n".join(formatted)
    except Exception as e:
        return f"Search error: {e}"

# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------
def outline_node(state: BriefState) -> dict:
    """Generate a 4‑5 item outline for the given topic."""
    chain = OUTLINE_PROMPT | LLM | StrOutputParser()
    outline_text = chain.invoke({"topic": state["topic"]})
    # Parse numbered list into a Python list
    lines = [line.strip() for line in outline_text.splitlines() if line.strip()]
    outline: List[str] = []
    for line in lines:
        # Remove leading numbers / bullets (e.g., "1. ")
        cleaned = line.lstrip("0123456789. ")
        if cleaned:
            outline.append(cleaned)
    # Fallback if parsing failed
    if len(outline) < 4:
        outline = [f"Point {i+1}" for i in range(4)]
    return {"outline": outline, "step_index": 0, "notes": []}


def research_step_node(state: BriefState) -> dict:
    """Research a single outline item, produce a short note, and advance the index."""
    idx = state["step_index"]
    outline_item = state["outline"][idx]
    # 1️⃣ Web search
    raw_results = tavily_search(outline_item)
    # 2️⃣ Summarise with LLM
    chain = NOTE_PROMPT | LLM | StrOutputParser()
    note = chain.invoke({"query": outline_item, "search_results": raw_results})
    # Update state
    new_notes = state["notes"] + [note]
    return {"notes": new_notes, "step_index": idx + 1}


def synthesize_node(state: BriefState) -> dict:
    """Combine all notes into a final brief with headings."""
    chain = SYNTHESIZE_PROMPT | LLM | StrOutputParser()
    brief = chain.invoke({
        "outline": "\n".join(state["outline"]),
        "notes": "\n\n".join(state["notes"]),
    })
    return {"final_brief": brief}

# ------------------------------------------------------------
# Graph construction
# ------------------------------------------------------------
workflow = StateGraph(BriefState)

# Nodes
workflow.add_node("outline", outline_node)
workflow.add_node("research", research_step_node)
workflow.add_node("synthesize", synthesize_node)

# Edges
workflow.add_edge(START, "outline")
workflow.add_edge("outline", "research")

# Conditional loop: continue researching until all outline items are processed
def should_continue(state: BriefState) -> str:
    if state["step_index"] < len(state["outline"]):
        return "research"
    return "synthesize"

workflow.add_conditional_edges(
    "research",
    should_continue,
    {"research": "research", "synthesize": "synthesize"},
)

workflow.add_edge("synthesize", END)

# Compile the graph (in‑memory checkpoint is enough for the demo)
graph = workflow.compile(checkpointer=MemoryCheckpoint())
# Expose the underlying workflow for tests that inspect nodes
graph.graph = workflow

# ------------------------------------------------------------
# Demo / CLI entry point
# ------------------------------------------------------------
DEFAULT_TOPIC = "Как студенту безопасно подключать MCP к LangChain"

def main(argv: Optional[List[str]] = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    topic_str = " ".join(args) if args else DEFAULT_TOPIC

    print(f"\n=== Research Brief for: {topic_str} ===\n")

    # Run the graph
    config = {"recursion_limit": 50}
    final_state = graph.invoke({"topic": topic_str}, config=config)

    # ---- Print results ----
    outline = final_state.get("outline", [])
    print("Outline:")
    for i, item in enumerate(outline, 1):
        print(f"{i}. {item}")
    print()

    notes = final_state.get("notes", [])
    for i, note in enumerate(notes, 1):
        print(f"[Шаг {i}] {note}\n")

    brief = final_state.get("final_brief", "")
    print("Final Brief:\n")
    print(brief)

if __name__ == "__main__":
    main()
