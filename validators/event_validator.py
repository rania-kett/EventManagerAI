"""
validators/event_validator.py — Validate event form submissions.
"""

from typing import Any, Dict, Tuple

from factories.event_factory import EventFactory

# Fields shown on the add-event form that must not be empty
ADD_EVENT_REQUIRED_FIELDS: Tuple[str, ...] = (
    "title",
    "date",
    "location",
    "category",
    "description",
)

_FIELD_LABELS = {
    "title": "Title",
    "date": "Date",
    "location": "Location",
    "category": "Category",
    "description": "Description",
}


class EventValidator:
    """Server-side validation for event forms."""

    @staticmethod
    def validate_add_event(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate POST data for creating an event.

        Returns:
            Dict mapping field name → error message (empty if valid).
        """
        errors: Dict[str, str] = {}

        for field in ADD_EVENT_REQUIRED_FIELDS:
            value = (data.get(field) or "").strip()
            if not value:
                label = _FIELD_LABELS.get(field, field.title())
                errors[field] = f"{label} is required."

        if "date" not in errors and (data.get("date") or "").strip():
            if EventFactory._parse_date(data.get("date")) is None:
                errors["date"] = "Enter a valid date."

        return errors

    @staticmethod
    def normalize_form_data(data: Dict[str, Any]) -> Dict[str, str]:
        """Strip values for re-rendering the form after validation errors."""
        return {
            field: (data.get(field) or "").strip()
            for field in ADD_EVENT_REQUIRED_FIELDS
        }
