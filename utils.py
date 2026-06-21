from typing import Any

from models import PersonInfo, MeetingNotes


def summarize(obj: Any) -> str:
    """Return a short human‑readable summary for a Pydantic model instance."""
    if isinstance(obj, PersonInfo):
        name = obj.name
        age = f", {obj.age}-year-old" if obj.age is not None else ""
        prof = obj.profession
        skills = ", ".join(obj.skills) if obj.skills else ""
        return f"Person {name}{age} {prof} with skills {skills}."
    if isinstance(obj, MeetingNotes):
        date = obj.date
        participants = ", ".join(obj.participants)
        decisions = ", ".join(obj.decisions) if obj.decisions else ""
        next_steps = ", ".join(obj.next_steps) if obj.next_steps else ""
        return (
            f"Meeting on {date} with participants {participants} – "
            f"decisions: {decisions}; next steps: {next_steps}."
        )
    return "No summary available."
