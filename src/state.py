from typing import TypedDict, Dict


class CodeReviewState(TypedDict, total=False):
    """State used by the LangGraph code‑review workflow.

    Fields:
        code: str – the source code to be reviewed.
        draft_review: str – the current review text.
        criteria_scores: dict[str, int] – scores for the four criteria.
        weakest_criterion: str – name of the criterion with the lowest score.
        verdict: str – "ok" or "needs_revision".
        round: int – current iteration number.
        max_rounds: int – maximum allowed iterations (default 2).
    """

    code: str
    draft_review: str
    criteria_scores: Dict[str, int]
    weakest_criterion: str
    verdict: str
    round: int
    max_rounds: int
