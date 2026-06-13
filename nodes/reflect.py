import json
from typing import Dict
from utils import get_llm, safe_json_parse


def reflect(state: Dict) -> Dict:
    """Critic node – scores the current draft review.

    Expected JSON output format:
    {
        "pep8": int, "type_hints": int, "edge_cases": int, "naming": int,
        "weakest_criterion": "pep8"|"type_hints"|"edge_cases"|"naming",
        "verdict": "ok"|"needs_revision"
    }
    """
    llm = get_llm()
    draft = state["draft_review"]
    prompt = (
        "You are an expert code reviewer. Evaluate the following code review and provide a JSON object "
        "with scores (0‑10) for each of the four criteria: pep8, type_hints, edge_cases, naming. "
        "Identify the criterion with the lowest score as \"weakest_criterion\". "
        "If all scores are >= 8, set verdict to \"ok\"; otherwise set it to \"needs_revision\". "
        "Return ONLY the JSON object, no extra text.\n\n"
        f"Review:\n{draft}\n"
    )
    response = llm.invoke([{"role": "user", "content": prompt}])
    raw = response.content
    try:
        data = safe_json_parse(raw)
    except ValueError as e:
        raise RuntimeError(f"Reflect node could not parse LLM output: {e}")

    # Ensure all required keys exist
    required = {"pep8", "type_hints", "edge_cases", "naming", "weakest_criterion", "verdict"}
    if not required.issubset(data.keys()):
        raise RuntimeError(f"Reflect node received incomplete data: {data}")

    # Update state
    state["criteria_scores"] = {
        "pep8": int(data["pep8"]),
        "type_hints": int(data["type_hints"]),
        "edge_cases": int(data["edge_cases"]),
        "naming": int(data["naming"]),
    }
    state["weakest_criterion"] = data["weakest_criterion"]
    state["verdict"] = data["verdict"]

    print("--- Critic Scores ---")
    print(
        f"pep8: {state['criteria_scores']['pep8']}, "
        f"type_hints: {state['criteria_scores']['type_hints']}, "
        f"edge_cases: {state['criteria_scores']['edge_cases']}, "
        f"naming: {state['criteria_scores']['naming']}"
    )
    print(f"Weakest criterion: {state['weakest_criterion']}")
    print(f"Verdict: {state['verdict']}")
    return state
