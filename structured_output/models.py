from pydantic import BaseModel, Field
from typing import List, Optional


class PersonInfo(BaseModel):
    """Information about a person."""
    name: str = Field(..., description="Full name of the person")
    age: Optional[int] = Field(None, description="Age of the person in years")
    profession: str = Field(..., description="Professional occupation of the person")
    skills: List[str] = Field(..., description="List of skills the person has")


class MeetingNotes(BaseModel):
    """Notes from a meeting."""
    date: str = Field(..., description="Date of the meeting")
    participants: List[str] = Field(..., description="Names of participants")
    topics: List[str] = Field(..., description="Topics discussed during the meeting")
    decisions: List[str] = Field(..., description="Decisions made in the meeting")
    next_steps: List[str] = Field(..., description="Next steps agreed upon")
