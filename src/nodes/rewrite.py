from typing import Dict

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


def rewrite(state: Dict) -> Dict:
    """Rewrite the part of the review that corresponds to the weakest criterion.

    The node updates ``draft_review`` and increments ``round``.
    """
    review = state.get("draft_review", "")
    weakest = state.get("weakest_criterion", "")
    if not review or not weakest:
        raise ValueError("Missing review or weakest_criterion for rewrite.")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    prompt = (
        f"You are a senior Python developer. The following code review has been critiqued as having a weak '{weakest}' aspect. "
        "Rewrite ONLY the part of the review that addresses this criterion, improving it while keeping the rest of the review unchanged. "
        "Return the full revised review (still as bullet points).\n\n"
        f"Current review:\n{review}\n"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    revised = response.content.strip()
    if not revised.startswith("-"):
        revised = "- " + revised.replace("\n", "\n- ")
    new_state = {
        "draft_review": revised,
        "round": state.get("round", 0) + 1,
    }
    print("\n=== Revised Review (round {} ) ===\n".format(new_state["round"]))
    print(revised, "\n")
    return new_state
