"""In-memory note storage. Intentionally no persistence."""

from datetime import datetime, timezone
from uuid import uuid4

from app.schemas import Note, NoteCreate


class NoteStore:
    def __init__(self) -> None:
        self._notes: dict[str, Note] = {}

    def add(self, data: NoteCreate) -> Note:
        note = Note(
            id=uuid4().hex,
            title=data.title,
            body=data.body,
            priority=data.priority,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._notes[note.id] = note
        return note

    def get(self, note_id: str) -> Note | None:
        return self._notes.get(note_id)

    def list(self) -> list[Note]:
        return list(self._notes.values())

    def clear(self) -> None:
        self._notes.clear()
