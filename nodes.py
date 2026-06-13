import os
import json
import ast
from typing import Dict, Any, List

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tavily import TavilyClient

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _load_llm() -> ChatOpenAI:
    """Create a ChatOpenAI instance.

    The function reads ``OPENAI_API_KEY`` from the environment (handled by
    ``python-dotenv`` in the CLI).  Temperature is set low for deterministic
    output when generating criteria and the final verdict.
    """
    return ChatOpenAI(temperature=0.2)


def _parse_list_response(text: str) -> List[str]:
    """Parse a LLM response that should contain a JSON/YAML list.

    The LLM is prompted to return a pure JSON list, but we defensively try
    ``json.loads`` first and fall back to ``ast.literal_eval``.
    """
    try:
        return json.loads(text)
    except Exception:
        try:
            return ast.literal_eval(text)
        except Exception:
            # As a last resort split on newlines/comma
            return [item.strip().strip('-').strip() for item in text.split('\n') if item.strip()]

# ---------------------------------------------------------------------------
# Node implementations – each receives the current state dict and returns a
# dict with the updates that should be merged back into the graph state.
# ---------------------------------------------------------------------------

def plan_criteria(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate 3‑5 comparison criteria based on the supplied entities.

    The LLM is asked to output a JSON list.  The resulting list is stored in
    ``state["criteria"]`` and an empty ``findings`` structure is prepared.
    """
    entities = state["entities"]
    prompt = (
        "You are an assistant that helps to compare several technologies. "
        "Given the following three entities, generate a concise list of 3 to 5 "
        "criteria that are useful for comparing them. Return the criteria as a "
        "JSON array of short strings (no extra text).\n\n"
        "Entities: {entities}\n"
    )
    tmpl = PromptTemplate.from_template(prompt)
    llm = _load_llm()
    chain_input = tmpl.format_prompt(entities=", ".join(entities)).to_messages()
    response = llm.invoke(chain_input)
    criteria = _parse_list_response(response.content)

    # Initialise findings dict – each entity gets a list with placeholders for each criterion
    findings: Dict[str, List[str]] = {entity: ["" for _ in criteria] for entity in entities}

    return {
        "criteria": criteria,
        "findings": findings,
        "current_pair": 0,  # start at the first pair
    }


def research_entity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Perform a Tavily search for the current (entity, criterion) pair.

    The function updates ``findings`` with a short note and increments the
    ``current_pair`` counter.
    """
    entities: List[str] = state["entities"]
    criteria: List[str] = state["criteria"]
    findings: Dict[str, List[str]] = state["findings"]
    pair_index: int = state["current_pair"]

    total_pairs = len(entities) * len(criteria)
    if pair_index >= total_pairs:
        # Nothing to do – the graph will move on.
        return {}

    # Determine which entity and which criterion we are processing.
    entity_idx = pair_index // len(criteria)
    criterion_idx = pair_index % len(criteria)
    entity = entities[entity_idx]
    criterion = criteria[criterion_idx]

    # Build a concise search query.
    query = f"{entity} {criterion}"  # simple concatenation works well for most cases

    # Initialise Tavily client.
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set in environment")
    client = TavilyClient(api_key=api_key)

    # Perform the search – we ask for a few results and pick the first useful snippet.
    try:
        results = client.search(query, max_results=5)
    except Exception as exc:
        # In case of network/API errors we store a placeholder note.
        note = f"Search failed: {exc}"
    else:
        # Extract a short description from the first result.
        if results and isinstance(results, list) and "snippet" in results[0]:
            snippet = results[0]["snippet"].strip()
            note = snippet if snippet else results[0].get("title", "No relevant info found")
        else:
            note = "No results returned"

    # Store the note in the correct cell.
    findings[entity][criterion_idx] = note

    # Increment the pair index for the next iteration.
    new_pair = pair_index + 1

    return {
        "findings": findings,
        "current_pair": new_pair,
    }


def build_table(state: Dict[str, Any]) -> Dict[str, Any]:
    """Create a markdown table from ``criteria`` and ``findings``.

    Rows correspond to criteria, columns to entities.  Cells contain the short
    notes collected by ``research_entity``.
    """
    entities: List[str] = state["entities"]
    criteria: List[str] = state["criteria"]
    findings: Dict[str, List[str]] = state["findings"]

    # Header row
    header = "| Criterion | " + " | ".join(entities) + " |"
    separator = "|---" + "|---" * len(entities) + "|"
    rows = [header, separator]

    for idx, crit in enumerate(criteria):
        cells = [findings[entity][idx].replace("|", "\\|") for entity in entities]
        row = f"| {crit} | " + " | ".join(cells) + " |"
        rows.append(row)

    table_md = "\n".join(rows)
    return {"final_table": table_md}


def verdict(state: Dict[str, Any]) -> Dict[str, Any]:
    """Ask the LLM to produce a short recommendation based on the table.
    """
    table = state.get("final_table", "")
    if not table:
        return {"verdict": "No table generated – cannot produce verdict."}

    prompt = (
        "You are an expert analyst. Based on the following comparison table, "
        "write a concise (2‑4 sentences) recommendation indicating which of the "
        "entities is best suited for which typical use‑case. Do not repeat the table, "
        "just give the verdict.\n\n{table}\n"
    )
    tmpl = PromptTemplate.from_template(prompt)
    llm = _load_llm()
    chain_input = tmpl.format_prompt(table=table).to_messages()
    response = llm.invoke(chain_input)
    verdict_text = response.content.strip()
    return {"verdict": verdict_text}
