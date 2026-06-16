from typing import TypedDict, Optional

class AgentState(TypedDict):
    """State of the self‑correcting agent."""
    task: str
    result: Optional[str]
    attempts: int
    status: str  # pending | success | failed | max_attempts
    error: Optional[str]
    max_attempts: int
