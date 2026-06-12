from typing import TypedDict, Dict


class CodeReviewState(TypedDict, total=False):
    """State model for the code‑review graph.

    All fields are optional because LangGraph updates the state incrementally.
    """

    code: str
    draft_review: str
    criteria_scores: Dict[str, int]  # e.g. {"pep8": 8, "type_hints": 5, ...}
    weakest_criterion: str
    verdict: str  # "ok" | "needs_revision"
    round: int
    max_rounds: int
