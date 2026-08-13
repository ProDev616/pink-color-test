import json

import pytest
from fastapi.testclient import TestClient

from app.ai.provider import AIProvider, AIProviderError
from app.dependencies import get_ai_provider
from app.main import app
from app.schemas import Note


class StubProvider(AIProvider):
    """Provider whose raw output (or failure) is scripted by the test."""

    def __init__(self, raw: str | None = None, error: Exception | None = None):
        self.raw = raw
        self.error = error

    def generate_analysis(self, note: Note) -> str:
        if self.error is not None:
            raise self.error
        assert self.raw is not None
        return self.raw


@pytest.fixture
def use_provider():
    def _use(provider: AIProvider) -> None:
        app.dependency_overrides[get_ai_provider] = lambda: provider

    yield _use
    app.dependency_overrides.pop(get_ai_provider, None)


def test_analyze_success_with_fake_provider(client: TestClient, note_id: str):
    # Uses the default FakeAIProvider; no network involved.
    response = client.post(f"/notes/{note_id}/analyze")
    assert response.status_code == 200
    analysis = response.json()
    assert set(analysis) == {"summary", "topics", "suggested_priority"}
    assert isinstance(analysis["summary"], str) and analysis["summary"]
    assert isinstance(analysis["topics"], list) and analysis["topics"]
    assert all(isinstance(topic, str) for topic in analysis["topics"])
    assert analysis["suggested_priority"] == "high"  # note text contains "urgent"/"deadline"


def test_analyze_success_with_scripted_provider(client: TestClient, note_id: str, use_provider):
    use_provider(
        StubProvider(
            raw=json.dumps(
                {"summary": "A short summary.", "topics": ["ml", "papers"], "suggested_priority": "low"}
            )
        )
    )
    response = client.post(f"/notes/{note_id}/analyze")
    assert response.status_code == 200
    assert response.json() == {
        "summary": "A short summary.",
        "topics": ["ml", "papers"],
        "suggested_priority": "low",
    }


def test_analyze_missing_note_returns_404(client: TestClient):
    response = client.post("/notes/does-not-exist/analyze")
    assert response.status_code == 404


def test_analyze_handles_non_json_output(client: TestClient, note_id: str, use_provider):
    use_provider(StubProvider(raw="Sure! Here is the analysis you asked for..."))
    response = client.post(f"/notes/{note_id}/analyze")
    assert response.status_code == 502
    assert response.json()["detail"] == "AI provider returned malformed output"


def test_analyze_handles_schema_violating_output(client: TestClient, note_id: str, use_provider):
    use_provider(
        StubProvider(raw=json.dumps({"summary": "ok", "topics": "not-a-list", "suggested_priority": "urgent"}))
    )
    response = client.post(f"/notes/{note_id}/analyze")
    assert response.status_code == 502
    assert response.json()["detail"] == "AI provider returned malformed output"


def test_analyze_handles_provider_error(client: TestClient, note_id: str, use_provider):
    use_provider(StubProvider(error=AIProviderError("upstream timeout")))
    response = client.post(f"/notes/{note_id}/analyze")
    assert response.status_code == 502
    assert response.json()["detail"] == "AI provider is unavailable"
