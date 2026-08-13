"""Real LLM provider example (not used in tests or CI).

Implements the same AIProvider interface as the fake, so swapping it in
only requires changing provider selection (see app.dependencies).
Requires `pip install openai` and an OPENAI_API_KEY environment variable.
"""

from app.ai.provider import AIProvider, AIProviderError
from app.schemas import Note

_PROMPT = (
    "Analyze the research note below. Respond with only a JSON object with keys: "
    '"summary" (short string), "topics" (array of strings), '
    '"suggested_priority" ("low", "medium" or "high").\n\n'
    "Title: {title}\n\nBody: {body}"
)


class OpenAIProvider(AIProvider):
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AIProviderError("openai package is not installed") from exc
        self._client = OpenAI()
        self._model = model

    def generate_analysis(self, note: Note) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": _PROMPT.format(title=note.title, body=note.body)}],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise AIProviderError(str(exc)) from exc
        content = response.choices[0].message.content
        if content is None:
            raise AIProviderError("empty response from OpenAI")
        return content
