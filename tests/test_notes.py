from fastapi.testclient import TestClient


def test_create_note_with_explicit_priority(client: TestClient):
    response = client.post(
        "/notes",
        json={"title": "Read paper", "body": "Skim the methods section.", "priority": "high"},
    )
    assert response.status_code == 201
    note = response.json()
    assert note["title"] == "Read paper"
    assert note["body"] == "Skim the methods section."
    assert note["priority"] == "high"
    assert note["id"]
    assert note["created_at"]


def test_priority_defaults_to_medium(client: TestClient):
    response = client.post("/notes", json={"title": "No priority", "body": "..."})
    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_invalid_priority_is_rejected(client: TestClient):
    response = client.post(
        "/notes",
        json={"title": "Bad", "body": "...", "priority": "extreme"},
    )
    assert response.status_code == 422


def test_list_notes_returns_created_notes(client: TestClient):
    client.post("/notes", json={"title": "One", "body": "a"})
    client.post("/notes", json={"title": "Two", "body": "b"})
    response = client.get("/notes")
    assert response.status_code == 200
    assert [note["title"] for note in response.json()] == ["One", "Two"]


def test_get_note_by_id(client: TestClient, note_id: str):
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id


def test_missing_note_returns_404(client: TestClient):
    response = client.get("/notes/does-not-exist")
    assert response.status_code == 404
