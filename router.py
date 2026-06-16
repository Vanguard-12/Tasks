from __future__ import annotations

from typing import Literal

# Simple keyword‑based routing. This is deterministic and does not require an extra LLM call.

_PERSON_KEYWORDS = {
    "name",
    "age",
    "profession",
    "skills",
    "developer",
    "engineer",
    "специалист",
    "работа",
    "работает",
    "ученый",
    "учитель",
}

_MEETING_KEYWORDS = {
    "date",
    "participants",
    "participants",
    "topic",
    "topics",
    "decision",
    "decisions",
    "next steps",
    "agenda",
    "meeting",
    "встреча",
    "принято решение",
}


def choose_schema(text: str) -> Literal["person", "meeting"]:
    """Return ``"person"`` if the text looks like a person description,
    otherwise ``"meeting"``.

    The function lower‑cases the input and checks for the presence of any
    keyword from the predefined sets. If both sets match (unlikely) the
    person schema wins because it is more specific for the assignment.
    """

    lowered = text.lower()
    person_hits = any(word in lowered for word in _PERSON_KEYWORDS)
    meeting_hits = any(word in lowered for word in _MEETING_KEYWORDS)

    if person_hits and not meeting_hits:
        return "person"
    if meeting_hits and not person_hits:
        return "meeting"
    # Fallback – decide based on which set has more hits
    person_score = sum(word in lowered for word in _PERSON_KEYWORDS)
    meeting_score = sum(word in lowered for word in _MEETING_KEYWORDS)
    return "person" if person_score >= meeting_score else "meeting"
