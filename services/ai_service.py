"""
services/ai_service.py — Gemini AI integration (future).

Isolates Google Generative AI from Flask routes. Configure via config.py:
  GEMINI_API_KEY, GEMINI_MODEL

Planned capability:
  generate_event_description(title, location, event_date, ...) → str

Install when implementing: google-generativeai (see requirements.txt).
"""

from typing import Any, Optional


class AIService:
    """
    Facade for Gemini API calls.

    Instantiate once per request or register as app extension later.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or ""
        self._model = model or "gemini-2.0-flash"
        self._client = None  # lazy init when google-generativeai is wired

    def is_configured(self) -> bool:
        """True when an API key is present."""
        return bool(self._api_key)

    def generate_event_description(
        self,
        title: str,
        location: Optional[str] = None,
        event_date: Optional[Any] = None,
        extra_context: Optional[str] = None,
    ) -> str:
        """
        Generate marketing-style event description using Gemini.

        Raises NotImplementedError until integration is complete.
        """
        if not self.is_configured():
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
            )

        # TODO: configure genai, build prompt, call model, return text
        raise NotImplementedError(
            "Gemini integration pending. See docs/ARCHITECTURE.md."
        )
