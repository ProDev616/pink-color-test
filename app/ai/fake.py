"""Deterministic fake provider that simulates LLM behavior without network calls."""

import json
import re

from app.ai.provider import AIProvider
from app.schemas import Note, Priority

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "is", "are", "was", "were", "this", "that", "it", "as", "at",
    "by", "be", "we", "i", "you",
}

_HIGH_SIGNALS = ("urgent", "asap", "deadline", "critical", "blocker", "important")
_LOW_SIGNALS = ("someday", "maybe", "idea", "optional", "backlog")


class FakeAIProvider(AIProvider):
    """Produces plausible, deterministic analysis derived from the note text."""

    def generate_analysis(self, note: Note) -> str:
        text = f"{note.title} {note.body}".lower()

        words = re.findall(r"[a-z]{4,}", text)
        topics: list[str] = []
        for word in words:
            if word not in _STOPWORDS and word not in topics:
                topics.append(word)
            if len(topics) == 3:
                break
        if not topics:
            topics = ["general"]

        if any(signal in text for signal in _HIGH_SIGNALS):
            suggested = Priority.HIGH
        elif any(signal in text for signal in _LOW_SIGNALS):
            suggested = Priority.LOW
        else:
            suggested = note.priority

        first_sentence = re.split(r"(?<=[.!?])\s+", note.body.strip())[0] if note.body.strip() else ""
        summary = f"{note.title.strip()}: {first_sentence}".strip(": ")
        if len(summary) > 200:
            summary = summary[:197] + "..."

        return json.dumps(
            {
                "summary": summary,
                "topics": topics,
                "suggested_priority": suggested.value,
            }
        )
