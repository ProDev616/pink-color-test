"""Validation layer between AI providers and the API.

Everything a provider returns is treated as untrusted: it must parse as
JSON and satisfy the NoteAnalysis schema before it reaches a response.
"""

import json
import logging

from pydantic import ValidationError

from app.ai.provider import AIProvider, AIProviderError
from app.schemas import Note, NoteAnalysis

logger = logging.getLogger(__name__)


class AnalysisError(Exception):
    """Raised when analysis could not be produced (provider failure or bad output)."""


def analyze_note(note: Note, provider: AIProvider) -> NoteAnalysis:
    try:
        raw = provider.generate_analysis(note)
    except AIProviderError as exc:
        logger.warning("AI provider failed for note %s: %s", note.id, exc)
        raise AnalysisError("AI provider is unavailable") from exc

    try:
        payload = json.loads(raw)
        return NoteAnalysis.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.warning("AI provider returned invalid output for note %s: %s", note.id, exc)
        raise AnalysisError("AI provider returned malformed output") from exc
