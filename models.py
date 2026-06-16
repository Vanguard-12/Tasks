from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PersonInfo(BaseModel):
    """Schema describing a person.

    All fields have a description to satisfy the assignment requirements.
    """

    name: str = Field(..., description="Full name of the person")
    age: Optional[int] = Field(
        None, description="Age of the person in years (optional)"
    )
    profession: str = Field(..., description="Professional title or occupation")
    skills: List[str] = Field(
        ..., description="A list of technical or soft skills"
    )


class MeetingNotes(BaseModel):
    """Schema describing meeting minutes.

    All fields have a description as required.
    """

    date: str = Field(..., description="Date of the meeting in ISO format (YYYY‑MM‑DD)")
    participants: List[str] = Field(
        ..., description="Names of participants attending the meeting"
    )
    topics: List[str] = Field(
        ..., description="Main topics that were discussed"
    )
    decisions: List[str] = Field(
        ..., description="Key decisions that were made during the meeting"
    )
    next_steps: List[str] = Field(
        ..., description="Action items or next steps agreed upon"
    )
