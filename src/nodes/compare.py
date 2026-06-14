import os
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from tavily import TavilyClient
from ..state import CompareState

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _init_llm() -> ChatOpenAI:
    """Create a ChatOpenAI instance.

    The model name can be overridden via the ``OPENAI_MODEL`` environment
    variable; otherwise we fall back to ``gpt-3.5-turbo`` which is cheap and
    sufficient for the demo.
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    return ChatOpenAI(model=model_name, temperature=0.7)


def _tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is not set in the environment")
    return TavilyClient(api_key=api_key)

# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def plan_criteria(state: CompareState) -> CompareState:
    """Generate 3‑5 comparison criteria for the supplied entities.

    The LLM receives a simple prompt and returns a JSON‑compatible list of
    strings.  We store the list in ``state['criteria']`` and initialise the
    ``findings`` dictionary with empty lists for each entity.
    """
    llm = _init_llm()
    prompt = PromptTemplate.from_template(
        """You are an analyst. Given the three entities below, propose a concise list of 3 to 5 criteria that are useful for comparing them.

        Entities:
        {entities}\n\nReturn the criteria as a JSON array, e.g. ['criterion 1', 'criterion 2', ...]."""
    )
    chain = prompt | llm
    response = chain.invoke({"entities": ", ".join(state["entities"])})
    # The LLM returns a string that looks like a Python list; ``eval`` is safe here
    # because the content is under our control.
    try:
        criteria = eval(response.content)  # type: ignore
    except Exception:
        # Fallback – split by newlines if the model didn't output JSON
        criteria = [c.strip("- ") for c in response.content.splitlines() if c.strip()]
    # Ensure we have at most 5 criteria
    criteria = criteria[:5]
    # Initialise findings dict
    findings: Dict[str, List[str]] = {entity: [] for entity in state["entities"]}
    # Initialise internal index
    state["criteria"] = criteria
    state["findings"] = findings
    state["pair_index"] = 0
    return state


def research_entity(state: CompareState) -> CompareState:
    """Perform a Tavily search for the current (entity, criterion) pair.

    The function extracts the appropriate entity and criterion based on the
    linear ``pair_index`` stored in the state, runs a single Tavily query, and
    stores a short note (first 200 characters of the first result) in the
    ``findings`` dictionary.
    """
    entities: List[str] = state["entities"]
    criteria: List[str] = state["criteria"]
    idx: int = state["pair_index"]
    total_pairs = len(entities) * len(criteria)
    if idx >= total_pairs:
        # Nothing to do – the graph should have moved on, but we guard against
        # accidental extra calls.
        return state

    entity_idx = idx // len(criteria)
    criterion_idx = idx % len(criteria)
    entity = entities[entity_idx]
    criterion = criteria[criterion_idx]

    client = _tavily_client()
    query = f"{entity} {criterion}"
    try:
        result = client.search(query, max_results=5)
    except Exception as exc:
        note = f"[Error during Tavily search: {exc}]"
    else:
        # Take the first result that contains a ``content`` field; fall back to URL.
        if result and isinstance(result, list) and "content" in result[0]:
            raw = result[0]["content"] or result[0].get("url", "")
        else:
            raw = result[0].get("url", "") if result else ""
        note = raw[:200].replace("\n", " ")
        if not note:
            note = "No relevant information found."

    # Append the note to the entity's list (maintaining order of criteria)
    state["findings"][entity].append(note)
    # Increment the pair index for the next iteration
    state["pair_index"] = idx + 1
    return state


def build_table(state: CompareState) -> CompareState:
    """Create a markdown table from ``state['findings']``.

    Rows correspond to criteria, columns to entities.  The function assumes that
    ``state['findings'][entity]`` contains a note for each criterion in the same
    order as ``state['criteria']``.
    """
    entities = state["entities"]
    criteria = state["criteria"]
    findings = state["findings"]

    # Header row
    header = "| Criterion | " + " | ".join(entities) + " |"
    separator = "|---" + "|---" * len(entities) + "|"
    rows = [header, separator]

    for i, crit in enumerate(criteria):
        cells = []
        for entity in entities:
            notes = findings.get(entity, [])
            note = notes[i] if i < len(notes) else ""
            # Escape pipe characters to keep markdown table valid
            note = note.replace("|", "\\|")
            cells.append(note)
        row = f"| {crit} | " + " | ".join(cells) + " |"
        rows.append(row)

    markdown = "\n".join(rows)
    state["final_table"] = markdown
    return state


def verdict(state: CompareState) -> CompareState:
    """Ask an LLM to produce a short recommendation based on the table.

    The prompt feeds the markdown table and asks for a 2‑4 sentence verdict.
    """
    llm = _init_llm()
    prompt = PromptTemplate.from_template(
        """You are an expert analyst. Based on the following comparison table, write a concise (2‑4 sentences) verdict that tells which of the listed entities is best suited for which use‑case.\n\n{table}\n\nProvide the answer without any extra formatting."""
    )
    chain = prompt | llm
    response = chain.invoke({"table": state.get("final_table", "")})
    state["verdict"] = response.content.strip()  # type: ignore
    return state
