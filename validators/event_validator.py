"""
validators/event_validator.py — Validate event form submissions.
"""

from typing import Any, Dict

from constants.event_form import EVENT_FIELD_LABELS, EVENT_FORM_FIELDS
from models.event_status import DEFAULT_STATUS, is_valid_status
from utils.dates import parse_event_date


class EventValidator:
    """Server-side validation for event forms."""

    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, str]:
        """Validate POST data; returns field name → error message."""
        errors = EventValidator._validate_required_fields(data)
        errors.update(EventValidator._validate_date_field(data, errors))
        errors.update(EventValidator._validate_status_field(data))
        return errors

    @staticmethod
    def normalize_form_data(data: Dict[str, Any]) -> Dict[str, str]:
        """Strip values for re-rendering the form after validation errors."""
        normalized = {
            field: (data.get(field) or "").strip()
            for field in EVENT_FORM_FIELDS
        }
        normalized["status"] = (data.get("status") or "").strip() or DEFAULT_STATUS
        return normalized

    @staticmethod
    def _validate_required_fields(data: Dict[str, Any]) -> Dict[str, str]:
        errors: Dict[str, str] = {}
        for field_name in EVENT_FORM_FIELDS:
            if not (data.get(field_name) or "").strip():
                label = EVENT_FIELD_LABELS.get(field_name, field_name.title())
                errors[field_name] = f"{label} obligatoire."
        return errors

    @staticmethod
    def _validate_date_field(
        data: Dict[str, Any], existing_errors: Dict[str, str]
    ) -> Dict[str, str]:
        if "date" in existing_errors or not (data.get("date") or "").strip():
            return {}
        if parse_event_date(data.get("date")) is None:
            return {"date": "Date invalide."}
        return {}

    @staticmethod
    def _validate_status_field(data: Dict[str, Any]) -> Dict[str, str]:
        status = (data.get("status") or "").strip()
        if not status:
            return {"status": f"{EVENT_FIELD_LABELS['status']} obligatoire."}
        if not is_valid_status(status):
            return {"status": "Statut invalide."}
        return {}
