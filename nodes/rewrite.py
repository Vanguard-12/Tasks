from typing import Dict
from utils import get_llm


def rewrite(state: Dict) -> Dict:
    """Rewrite the part of the draft review that corresponds to the weakest criterion.

    The function increments ``state['round']`` and replaces ``state['draft_review']`` with the
    revised version.
    """
    llm = get_llm()
    draft = state["draft_review"]
    weakest = state["weakest_criterion"]
    prompt = (
        "You are a senior Python developer. Improve ONLY the part of the following code review that "
        f"addresses **{weakest}**. Keep the rest of the review unchanged. Return the full revised review "
        "as plain text (no JSON, no extra explanations).\n\n"
        f"Current review:\n{draft}\n"
    )
    response = llm.invoke([{"role": "user", "content": prompt}])
    revised = response.content.strip()
    state["draft_review"] = revised
    state["round"] += 1
    print(f"--- Rewrite (round {state['round']}) – focusing on {weakest} ---")
    print(revised)
    return state
