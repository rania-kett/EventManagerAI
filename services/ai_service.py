"""
services/ai_service.py — Gemini AI integration for event descriptions.
"""

from typing import Any, List, Mapping, Optional

try:
    from google import genai
except ImportError:  # pragma: no cover
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
        cleaned_title = (title or "").strip()
        self._ensure_ready(cleaned_title)

        prompt = self._build_prompt(
            title=cleaned_title,
            location=location,
            event_date=event_date,
            category=category,
        )
        return self._request_description(prompt)

    def _ensure_ready(self, title: str) -> None:
        if not title:
            raise AIServiceError("Event title is required for AI generation.")
        if not self.is_configured():
            raise AIServiceNotConfiguredError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        if genai is None:
            raise AIServiceError(
                "google-genai is not installed. Run: pip install google-genai"
            )

    @staticmethod
    def _build_prompt(
        *,
        title: str,
        location: Optional[str],
        event_date: Optional[Any],
        category: Optional[str],
    ) -> str:
        context_lines = [f"Event title: {title}"]
        if category:
            context_lines.append(f"Category: {category.strip()}")
        if location:
            context_lines.append(f"Location: {location.strip()}")
        if event_date:
            context_lines.append(f"Date: {event_date}")

        instructions = (
            "You are a professional event marketing copywriter.\n"
            "Write an elegant, engaging event description in French (2–4 short paragraphs).\n"
            "Tone: premium, professional, suitable for a high-end event agency.\n"
            "Do not use bullet points or markdown headings. Return plain text only.\n\n"
        )
        return instructions + "\n".join(context_lines)

    def _request_description(self, prompt: str) -> str:
        client = genai.Client(api_key=self._api_key)

        try:
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
            text = (response.text or "").strip()
        except Exception as exc:
            raise self._map_provider_error(exc) from exc

        if not text:
            raise AIServiceError("Gemini returned an empty description.")
        return text

    def _map_provider_error(self, exc: Exception) -> AIServiceError:
        error_message = str(exc)
        if "429" in error_message or "quota" in error_message.lower():
            return AIServiceError(
                "Quota Gemini dépassé pour ce modèle. "
                "Changez GEMINI_MODEL=gemini-2.5-flash dans .env "
                "et redémarrez l'application."
            )
        if "404" in error_message and "not found" in error_message.lower():
            return AIServiceError(
                f"Modèle « {self._model} » introuvable. "
                "Utilisez GEMINI_MODEL=gemini-2.5-flash dans .env."
            )
        return AIServiceError(f"Erreur Gemini : {error_message}")
