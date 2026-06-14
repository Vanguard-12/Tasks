import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from ..utils import safe_json_load

CRITERIA = ["pep8", "type_hints", "edge_cases", "naming"]


def reflect(state: Dict) -> Dict:
    """Score the current draft review on four criteria.

    Returns updated ``criteria_scores``, ``weakest_criterion`` and ``verdict``.
    """
    review = state.get("draft_review", "")
    if not review:
        raise ValueError("draft_review missing for reflection.")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
    prompt = (
        "You are a code‑review critic. Score the following review on four criteria: "
        "PEP8, type hints, edge cases, and naming. Provide a JSON object with keys "
        "'pep8', 'type_hints', 'edge_cases', 'naming' each having an integer score 0‑10. "
        "Also include a field 'verdict' with value 'ok' if all scores are >=7, otherwise 'needs_revision'. "
        "Example: {\"pep8\": 8, \"type_hints\": 6, \"edge_cases\": 7, \"naming\": 9, \"verdict\": \"needs_revision\"}.\n\n"
        f"Review:\n{review}\n"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()
    data = safe_json_load(raw)
    if not isinstance(data, dict):
        raise ValueError("Failed to parse critic JSON output.")

    # Ensure all criteria present
    scores = {c: int(data.get(c, 0)) for c in CRITERIA}
    verdict = data.get("verdict", "needs_revision")
    # Determine weakest criterion (lowest score, tie‑break by order)
    weakest = min(scores, key=lambda k: scores[k])

    new_state = {
        "criteria_scores": scores,
        "weakest_criterion": weakest,
        "verdict": verdict,
    }
    print("\n=== Critic Scores ===")
    for crit, sc in scores.items():
        print(f"{crit}: {sc}")
    print("Verdict:", verdict)
    print("Weakest criterion:", weakest, "\n")
    return new_state
