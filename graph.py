import json
from typing import Tuple, List, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearchResults
from state import CompareState

# LLM used for both planning and verdict
llm = ChatOpenAI(model="gpt-4o-mini")

def _init_pending(state: CompareState) -> CompareState:
    # create list of all (entity, criterion) pairs
    state['_pending_pairs'] = [(e, c) for e in state['entities'] for c in state['criteria']]
    return state

async def plan_criteria(state: CompareState) -> CompareState:
    prompt = (
        "You are given three entities that need to be compared. Generate a concise list of 3 to 5 criteria that are relevant for comparing them. "
        "Return the criteria as a JSON array of strings.\n"
        f"Entities: {json.dumps(state['entities'])}"
    )
    response = await llm.ainvoke(prompt)
    try:
        criteria = json.loads(response.content)
    except Exception:
        # fallback: split lines
        criteria = [c.strip() for c in response.content.split('\n') if c.strip()]
    state['criteria'] = criteria[:5]
    return _init_pending(state)

async def research_entity(state: CompareState) -> CompareState:
    if not state['_pending_pairs']:
        return state
    entity, criterion = state['_pending_pairs'].pop(0)
    query = f"{entity} {criterion}"
    tavily = TavilySearchResults()
    results = await tavily.ainvoke({"query": query, "max_results": 3})
    # Take first result's content or title
    note = results[0].get('content') or results[0].get('title') or "No concise info found."
    short_note = note.split('\n')[0][:200]
    state.setdefault('findings', {}).setdefault(entity, []).append(short_note)
    return state

async def build_table(state: CompareState) -> CompareState:
    header = "| Criterion | " + " | ".join(state['entities']) + " |"
    separator = "|---" + "|---" * len(state['entities']) + "|"
    rows: List[str] = []
    for idx, crit in enumerate(state['criteria']):
        cells = []
        for ent in state['entities']:
            notes = state['findings'].get(ent, [])
            note = notes[idx] if idx < len(notes) else "-"
            cells.append(note.replace("|", "\\|"))
        rows.append(f"| {crit} | " + " | ".join(cells) + " |")
    table = "\n".join([header, separator] + rows)
    state['final_table'] = table
    return state

async def verdict(state: CompareState) -> CompareState:
    prompt = (
        "Based on the following comparison table, write 2-4 sentences recommending which entity is best suited for which use‑case.\n\n"
        f"{state['final_table']}"
    )
    response = await llm.ainvoke(prompt)
    state['verdict'] = response.content.strip()
    return state

# Build graph
workflow = StateGraph(CompareState)
workflow.add_node("plan_criteria", plan_criteria)
workflow.add_node("research_entity", research_entity)
workflow.add_node("build_table", build_table)
workflow.add_node("verdict", verdict)

workflow.set_entry_point("plan_criteria")
workflow.add_edge("plan_criteria", "research_entity")
workflow.add_conditional_edges(
    "research_entity",
    lambda s: "research_entity" if s.get('_pending_pairs') else "build_table",
)
workflow.add_edge("build_table", "verdict")
workflow.add_edge("verdict", END)

graph = workflow.compile()
