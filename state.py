from typing import TypedDict, List, Dict, Optional, Tuple

class CompareState(TypedDict):
    entities: List[str]
    criteria: List[str]
    findings: Dict[str, List[str]]
    final_table: Optional[str]
    verdict: Optional[str]
    _pending_pairs: List[Tuple[str, str]]
