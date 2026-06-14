import re
from typing import Tuple

from .models import PersonInfo, MeetingNotes
from .extractor import get_chain

PERSON_KEYWORDS = [
    "имя",
    "возраст",
    "профессия",
    "навыки",
    "skill",
    "age",
    "profession",
]
MEETING_KEYWORDS = [
    "встреча",
    "дата",
    "участники",
    "темы",
    "решения",
    "next",
    "steps",
    "agenda",
]


def select_model(text: str):
    lowered = text.lower()
    person_score = sum(1 for kw in PERSON_KEYWORDS if kw in lowered)
    meeting_score = sum(1 for kw in MEETING_KEYWORDS if kw in lowered)
    if person_score > meeting_score:
        return PersonInfo
    else:
        return MeetingNotes


def get_chain_for_text(text: str) -> Tuple["Runnable", type]:
    """Return the appropriate chain and the model class for the given text."""
    model_cls = select_model(text)
    chain = get_chain(model_cls)
    return chain, model_cls
