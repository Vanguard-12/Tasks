from typing import TypedDict

class ReflectState(TypedDict):
    """State used by the LangGraph reflection agent."""
    question: str
    draft: str
    critique: str
    verdict: str  # "ok" or "needs_revision"
    round: int
    max_rounds: int
