"""
ai_handlers.py — JSON responses for Gemini description endpoints.
"""

from typing import Any, Dict, Mapping, Tuple

from flask import current_app

from services.ai_service import (
    AIService,
    AIServiceError,
    AIServiceNotConfiguredError,
)
from services.event_service import EventService

JsonResponse = Tuple[Dict[str, Any], int]


def parse_ai_payload(request) -> Dict[str, Any]:
    """Read JSON or form body for AI generation."""
    return request.get_json(silent=True) or request.form


def build_ai_service() -> AIService:
    return AIService.from_config(current_app.config)


def generate_description_response(payload: Mapping[str, Any]) -> JsonResponse:
    """Generate description from title/location/date/category (no DB write)."""
    title = (payload.get("title") or "").strip()
    if not title:
        return {"success": False, "message": "Le titre est obligatoire."}, 400

    return _run_ai_generation(
        title=title,
        location=_optional_field(payload, "location"),
        event_date=_optional_field(payload, "date"),
        category=_optional_field(payload, "category"),
    )


def generate_and_save_description_response(event) -> JsonResponse:
    """Generate description for an existing event and persist it."""
    return _run_ai_generation(
        title=event.title,
        location=event.location,
        event_date=event.date.isoformat() if event.date else None,
        category=event.category,
        on_success=lambda description: EventService.save_description(
            event, description
        ),
    )


def _optional_field(payload: Mapping[str, Any], key: str):
    value = (payload.get(key) or "").strip()
    return value or None


def _run_ai_generation(
    *,
    title: str,
    location: str | None,
    event_date: str | None,
    category: str | None,
    on_success=None,
) -> JsonResponse:
    ai_service = build_ai_service()
    try:
        description = EventService.generate_description_with_ai(
            ai_service,
            title=title,
            location=location,
            event_date=event_date,
            category=category,
        )
        if on_success:
            on_success(description)
    except AIServiceNotConfiguredError as exc:
        return {"success": False, "message": str(exc)}, 503
    except AIServiceError as exc:
        return {"success": False, "message": str(exc)}, 502

    return {"success": True, "description": description}, 200
