from typing import List, Optional

from pydantic import BaseModel, Field


class PersonInfo(BaseModel):
    """Schema describing a person."""

    name: str = Field(..., description="Full name of the person")
    age: Optional[int] = Field(
        None, description="Age of the person in years (optional)"
    )
    profession: str = Field(..., description="Professional title or occupation")
    skills: List[str] = Field(..., description="List of technical or soft skills")


class MeetingNotes(BaseModel):
    """Schema describing meeting notes."""

    date: str = Field(..., description="Date of the meeting in ISO format (YYYY-MM-DD)")
    participants: List[str] = Field(
        ..., description="Names of participants attending the meeting"
    )
    topics: List[str] = Field(..., description="List of topics discussed during the meeting")
    decisions: List[str] = Field(..., description="Decisions made in the meeting")
    next_steps: List[str] = Field(
        ..., description="Action items or next steps agreed upon"
    )
