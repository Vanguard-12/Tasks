from typing import TypedDict, Dict


class CodeReviewState(TypedDict):
    """State container for the LangGraph code‑review workflow.

    Fields correspond exactly to the specification in the assignment.
    """

    code: str
    draft_review: str
    criteria_scores: Dict[str, int]  # e.g. {"pep8": 8, "type_hints": 5, ...}
    weakest_criterion: str
    verdict: str  # "ok" | "needs_revision"
    round: int
    max_rounds: int
