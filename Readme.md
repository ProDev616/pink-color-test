# Research Notes API

A small FastAPI service for managing research notes with AI-assisted analysis.
Notes are stored **in memory only** — restarting the server clears them.

## Endpoints

| Method | Path                  | Description                                        |
| ------ | --------------------- | -------------------------------------------------- |
| POST   | `/notes`              | Create a note (`priority` defaults to `medium`)    |
| GET    | `/notes`              | List all notes                                     |
| GET    | `/notes/{id}`         | Get one note, `404` if not found                   |
| POST   | `/notes/{id}/analyze` | AI analysis: summary, topics, suggested priority   |

Invalid `priority` values (anything other than `low`/`medium`/`high`) are
rejected with a `422`.

## AI integration boundary

The analyze endpoint talks to an `AIProvider` (`app/ai/provider.py`), whose
contract is deliberately narrow: it takes a note and returns the **raw text**
an LLM produced. Everything a provider returns is treated as untrusted —
`app/ai/service.py` parses it as JSON and validates it against the
`NoteAnalysis` schema before it can reach a response.

Failure handling:

- Provider raises (timeout, API error, ...) → `502 AI provider is unavailable`
- Output is not JSON or violates the schema → `502 AI provider returned malformed output`

Two providers are included:

- `FakeAIProvider` (default): deterministic, no network. Used by the app,
  the tests, and CI.
- `OpenAIProvider` (example, never used in tests/CI): set
  `AI_PROVIDER=openai` and `OPENAI_API_KEY`, and `pip install openai`.

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive docs at http://127.0.0.1:8000/docs.

## Testing

Tests never make external requests: the analyze tests use the fake provider
or per-test stub providers injected via FastAPI dependency overrides.

```bash
pip install -r requirements-dev.txt
pytest
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs the test suite on every
pull request (and pushes to `main`). No AI credentials are required.
