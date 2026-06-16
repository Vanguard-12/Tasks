from typing import TypedDict


class ReflectState(TypedDict):
    """State carried through the LangGraph workflow.

    - ``question``: the original user question.
    - ``draft``: current answer draft (populated by ``draft_answer`` and ``rewrite``).
    - ``critique``: text produced by the ``reflect`` node.
    - ``verdict``: either ``"ok"`` or ``"needs_revision"``.
    - ``round``: current revision round (starts at 0).
    - ``max_rounds``: maximum allowed revision rounds (default 2).
    """

    question: str
    draft: str
    critique: str
    verdict: str  # "ok" | "needs_revision"
    round: int
    max_rounds: int
