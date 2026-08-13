"""AI provider boundary.

Providers return the *raw text* an LLM produced. Parsing and schema
validation happen on our side of the boundary (see app/ai/service.py),
so a misbehaving provider can never inject an unvalidated payload into
the API response.
"""

from abc import ABC, abstractmethod

from app.schemas import Note


class AIProviderError(Exception):
    """Raised when a provider fails to produce output (timeout, API error, ...)."""


class AIProvider(ABC):
    @abstractmethod
    def generate_analysis(self, note: Note) -> str:
        """Return raw model output, expected to be a JSON object with
        `summary`, `topics` and `suggested_priority` keys.

        Raises AIProviderError on provider-side failure.
        """
