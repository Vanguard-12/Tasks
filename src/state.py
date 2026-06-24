from typing import TypedDict

class ReflectState(TypedDict):
    question: str
    draft: str
    critique: str
    verdict: str  # ok | needs_revision
    round: int
    max_rounds: int
