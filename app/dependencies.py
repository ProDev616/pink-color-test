"""Dependency wiring. Tests override these via app.dependency_overrides."""

import os

from app.ai.fake import FakeAIProvider
from app.ai.provider import AIProvider
from app.store import NoteStore

_store = NoteStore()
_fake_provider = FakeAIProvider()


def get_store() -> NoteStore:
    return _store


def get_ai_provider() -> AIProvider:
    # Opt in to a real LLM only when explicitly configured; the fake
    # provider is the default so tests and CI never need credentials.
    if os.environ.get("AI_PROVIDER") == "openai":
        from app.ai.openai_provider import OpenAIProvider

        return OpenAIProvider()
    return _fake_provider
