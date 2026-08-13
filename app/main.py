from fastapi import Depends, FastAPI, HTTPException

from app.ai.provider import AIProvider
from app.ai.service import AnalysisError, analyze_note
from app.dependencies import get_ai_provider, get_store
from app.schemas import Note, NoteAnalysis, NoteCreate
from app.store import NoteStore

app = FastAPI(title="Research Notes API")


def _get_note_or_404(store: NoteStore, note_id: str) -> Note:
    note = store.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.post("/notes", response_model=Note, status_code=201)
def create_note(data: NoteCreate, store: NoteStore = Depends(get_store)) -> Note:
    return store.add(data)


@app.get("/notes", response_model=list[Note])
def list_notes(store: NoteStore = Depends(get_store)) -> list[Note]:
    return store.list()


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str, store: NoteStore = Depends(get_store)) -> Note:
    return _get_note_or_404(store, note_id)


@app.post("/notes/{note_id}/analyze", response_model=NoteAnalysis)
def analyze(
    note_id: str,
    store: NoteStore = Depends(get_store),
    provider: AIProvider = Depends(get_ai_provider),
) -> NoteAnalysis:
    note = _get_note_or_404(store, note_id)
    try:
        return analyze_note(note, provider)
    except AnalysisError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
