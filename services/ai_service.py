"""
services/ai_service.py — Gemini AI integration for event descriptions.

Isolated from Flask routes. Configure via config.py:
  GEMINI_API_KEY, GEMINI_MODEL
"""

from typing import Any, Mapping, Optional

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional until pip install
    genai = None  # type: ignore


class AIServiceError(Exception):
    """Raised when AI generation fails."""


class AIServiceNotConfiguredError(AIServiceError):
    """Raised when GEMINI_API_KEY is missing."""


class AIService:
    """Facade for Google Gemini API calls."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = (api_key or "").strip()
        self._model = model or "gemini-2.5-flash"

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "AIService":
        """Build service from Flask app.config."""
        return cls(
            api_key=config.get("GEMINI_API_KEY"),
            model=config.get("GEMINI_MODEL"),
        )

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate_event_description(
        self,
        title: str,
        location: Optional[str] = None,
        event_date: Optional[Any] = None,
        category: Optional[str] = None,
    ) -> str:
        """
        Generate a professional marketing description for an event.

        Args:
            title: Event title (required).
            location: Optional venue or city.
            event_date: Optional date string or date object.
            category: Optional event type/category.

        Returns:
            Generated description text.
        """
        title = (title or "").strip()
        if not title:
            raise AIServiceError("Event title is required for AI generation.")

        if not self.is_configured():
            raise AIServiceNotConfiguredError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

        if genai is None:
            raise AIServiceError(
                "google-generativeai is not installed. Run: pip install google-generativeai"
            )

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(self._model)

        context_lines = [f"Event title: {title}"]
        if category:
            context_lines.append(f"Category: {category.strip()}")
        if location:
            context_lines.append(f"Location: {location.strip()}")
        if event_date:
            context_lines.append(f"Date: {event_date}")

        prompt = (
            "You are a professional event marketing copywriter.\n"
            "Write an elegant, engaging event description in French (2–4 short paragraphs).\n"
            "Tone: premium, professional, suitable for a high-end event agency.\n"
            "Do not use bullet points or markdown headings. Return plain text only.\n\n"
            + "\n".join(context_lines)
        )

        try:
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
        except Exception as exc:
            err_msg = str(exc)
            if "429" in err_msg or "quota" in err_msg.lower():
                raise AIServiceError(
                    "Quota Gemini dépassé pour ce modèle. "
                    "Changez GEMINI_MODEL=gemini-2.5-flash dans .env et redémarrez l'application."
                ) from exc
            if "404" in err_msg and "not found" in err_msg.lower():
                raise AIServiceError(
                    f"Modèle « {self._model} » introuvable. "
                    "Utilisez GEMINI_MODEL=gemini-2.5-flash dans .env."
                ) from exc
            raise AIServiceError(f"Erreur Gemini : {err_msg}") from exc

        if not text:
            raise AIServiceError("Gemini returned an empty description.")

        return text
