from typing import Dict
from utils import get_llm


def draft_review(state: Dict) -> Dict:
    """Generate an initial 3‑6 bullet code review for ``state['code']``.

    The function updates ``state['draft_review']`` and returns the modified state.
    """
    llm = get_llm()
    code = state["code"]
    prompt = (
        "You are a senior Python developer. Write a concise code review (3‑6 bullet points) "
        "for the following function. Focus on clarity, correctness, PEP8 compliance, type hints, "
        "edge‑case handling and naming. Do NOT include any explanations beyond the bullet list.\n\n"
        f"```python\n{code}\n```"
    )
    response = llm.invoke([{"role": "user", "content": prompt}])
    review = response.content.strip()
    state["draft_review"] = review
    print("--- Draft Review ---")
    print(review)
    return state
