import os
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables (API keys, etc.)
load_dotenv()

# Choose LLM – OpenAI if key present, otherwise Ollama (via OpenAI compatible endpoint)
if os.getenv("OPENAI_API_KEY"):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
else:
    # Ollama – we rely on the OpenAI compatible endpoint
    llm = ChatOpenAI(base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                     model="llama3", temperature=0.7)


def draft_review(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an initial code review (3‑6 bullet points).

    The function receives the current state, expects ``code`` to be present and
    returns a dict with the new ``draft_review``.
    """
    code = state.get("code", "")
    system_prompt = (
        "You are a senior Python developer. Review the following function and "
        "provide a concise review consisting of 3‑6 bullet points. Focus on "
        "PEP8 style, type hints, edge‑case handling and naming. Do NOT suggest "
        "any changes yet – just list observations."
    )
    user_prompt = f"```python\n{code}\n```"
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    draft = response.content.strip()
    return {"draft_review": draft}


def reflect(state: Dict[str, Any]) -> Dict[str, Any]:
    """Critic node – score the draft review on four criteria.

    Returns ``criteria_scores`` (dict), ``weakest_criterion`` (str), ``verdict``
    ("ok" or "needs_revision").
    """
    draft = state.get("draft_review", "")
    system_prompt = (
        "You are a code‑review critic. Evaluate the following review and "
        "provide a JSON object with the following keys: \n"
        "  - scores: an object with keys 'pep8', 'type_hints', 'edge_cases', "
        "    'naming' each having an integer 0‑10,\n"
        "  - weakest_criterion: the key with the lowest score,\n"
        "  - verdict: 'ok' if all scores are >=7, otherwise 'needs_revision'.\n"
        "Return ONLY the JSON object, no extra text."
    )
    user_prompt = f"Review to evaluate:\n{draft}"
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback – if the model adds extra text, try to extract the JSON block
        import re
        match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            # Very defensive default – treat as needs revision with low scores
            data = {
                "scores": {"pep8": 0, "type_hints": 0, "edge_cases": 0, "naming": 0},
                "weakest_criterion": "pep8",
                "verdict": "needs_revision",
            }
    scores: Dict[str, int] = data.get("scores", {})
    # Determine weakest criterion (first with minimal score if tie)
    if scores:
        min_score = min(scores.values())
        weakest = next(k for k, v in scores.items() if v == min_score)
    else:
        weakest = "pep8"
    verdict = data.get("verdict", "needs_revision")
    return {
        "criteria_scores": scores,
        "weakest_criterion": weakest,
        "verdict": verdict,
    }


def rewrite(state: Dict[str, Any]) -> Dict[str, Any]:
    """Rewrite the part of the draft review that corresponds to the weakest criterion.

    The node increments ``round`` and returns an updated ``draft_review``.
    """
    draft = state.get("draft_review", "")
    weakest = state.get("weakest_criterion", "pep8")
    round_no = state.get("round", 0) + 1
    system_prompt = (
        "You are a helpful assistant that improves a code‑review. The review "
        "contains several bullet points. Rewrite ONLY the bullet point(s) that "
        f"address the criterion '{weakest}'. Keep the rest of the review unchanged."
    )
    user_prompt = f"Current review:\n{draft}"
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    new_draft = response.content.strip()
    return {"draft_review": new_draft, "round": round_no}
