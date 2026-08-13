import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_store
from app.main import app
from app.store import NoteStore


@pytest.fixture
def client() -> TestClient:
    """Test client with a fresh in-memory store per test."""
    store = NoteStore()
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def note_id(client: TestClient) -> str:
    response = client.post(
        "/notes",
        json={"title": "Urgent literature review", "body": "Summarize recent papers before the deadline."},
    )
    assert response.status_code == 201
    return response.json()["id"]
