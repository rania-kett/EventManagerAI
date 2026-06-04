"""
validators/event_validator.py — Validate event form submissions.
"""

from typing import Any, Dict, Tuple

from factories.event_factory import EventFactory

# Champs obligatoires sur les formulaires création / édition
EVENT_REQUIRED_FIELDS: Tuple[str, ...] = (
    "title",
    "date",
    "location",
    "category",
    "description",
)

# Alias rétrocompatible
ADD_EVENT_REQUIRED_FIELDS = EVENT_REQUIRED_FIELDS

_FIELD_LABELS = {
    "title": "Titre",
    "date": "Date",
    "location": "Lieu",
    "category": "Catégorie",
    "description": "Description",
}


class EventValidator:
    """Server-side validation for event forms."""

    @staticmethod
    def validate_event_form(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate POST data for creating or updating an event.

        Returns:
            Dict mapping field name → error message (empty if valid).
        """
        errors: Dict[str, str] = {}

        for field in EVENT_REQUIRED_FIELDS:
            value = (data.get(field) or "").strip()
            if not value:
                label = _FIELD_LABELS.get(field, field.title())
                errors[field] = f"{label} obligatoire."

        if "date" not in errors and (data.get("date") or "").strip():
            if EventFactory._parse_date(data.get("date")) is None:
                errors["date"] = "Date invalide."

        return errors

    @staticmethod
    def validate_add_event(data: Dict[str, Any]) -> Dict[str, str]:
        """Alias pour la création d'événement."""
        return EventValidator.validate_event_form(data)

    @staticmethod
    def validate_edit_event(data: Dict[str, Any]) -> Dict[str, str]:
        """Alias pour la modification d'événement."""
        return EventValidator.validate_event_form(data)

    @staticmethod
    def normalize_form_data(data: Dict[str, Any]) -> Dict[str, str]:
        """Strip values for re-rendering the form after validation errors."""
        return {
            field: (data.get(field) or "").strip()
            for field in EVENT_REQUIRED_FIELDS
        }
