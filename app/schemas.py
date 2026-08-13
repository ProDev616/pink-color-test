"""Pydantic models shared across the API and the AI boundary."""

from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    body: str
    priority: Priority = Priority.MEDIUM


class Note(BaseModel):
    id: str
    title: str
    body: str
    priority: Priority
    created_at: str


class NoteAnalysis(BaseModel):
    """Validated shape of an AI provider's analysis output."""

    summary: str
    topics: list[str]
    suggested_priority: Priority
