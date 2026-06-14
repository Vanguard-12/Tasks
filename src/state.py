from typing import TypedDict, List, Dict, Optional


class CompareState(TypedDict, total=False):
    """State model for the comparison workflow.

    The fields listed in the assignment are required, but we also keep a few
    internal helpers (pair_index) that are not part of the public contract.
    """

    # Public fields required by the task
    entities: List[str]                # three entities to compare
    criteria: List[str]                # 3‑5 generated criteria
    findings: Dict[str, List[str]]     # entity -> list of notes (one per criterion)
    final_table: Optional[str]        # markdown table produced at the end
    verdict: Optional[str]            # short recommendation produced by LLM

    # Internal helpers (not part of the spec but useful for the graph)
    pair_index: int                    # linear index of the current (entity, criterion) pair
