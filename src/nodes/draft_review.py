import json
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from ..utils import safe_json_load


def draft_review(state: Dict) -> Dict:
    """Generate a short bullet‑point review for the supplied code.

    The node updates ``draft_review`` in the state and returns the new state.
    """
    code = state.get("code", "")
    if not code:
        raise ValueError("No code provided in state.")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    prompt = (
        "You are a senior Python developer. Write a concise code review for the following function. "
        "Provide 3‑6 bullet points, each focusing on style, correctness, performance, or readability. "
        "Do not include any explanations beyond the bullet points.\n\n"
        f"```python\n{code}\n```"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    review_text = response.content.strip()
    # Ensure we have bullet points – simple fallback if LLM returns plain text
    if not review_text.startswith("-"):
        review_text = "- " + review_text.replace("\n", "\n- ")
    new_state = {
        "draft_review": review_text,
        "round": state.get("round", 0) + 1,  # first round after draft
    }
    print("\n=== Draft Review ===\n", review_text, "\n")
    return new_state
