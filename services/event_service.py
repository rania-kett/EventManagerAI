"""
services/event_service.py — Event use cases (create, update, delete).
"""

from typing import Any, Dict, Optional, Tuple

from factories.event_factory import EventFactory
from models import db
from models.event import Event
from models.event_status import DEFAULT_STATUS, STATUS_LABELS, is_valid_status
from validators.event_validator import EventValidator


class EventService:
    """Orchestrates validation, factories, and database persistence."""

    @staticmethod
    def create_from_form(
        data: Dict[str, Any],
    ) -> Tuple[Optional[Event], Dict[str, str], Dict[str, str]]:
        """
        Validate form data, persist a new event, and return result metadata.

        Returns:
            (event, errors, form_data)
            - event is set on success; errors is non-empty on failure
            - form_data holds stripped values for re-displaying the form
        """
        form_data = EventValidator.normalize_form_data(data)
        errors = EventValidator.validate_add_event(data)

        if errors:
            return None, errors, form_data

        event = EventFactory.from_form(data)
        db.session.add(event)
        db.session.commit()
        return event, {}, form_data

    @staticmethod
    def event_to_form(event: Event) -> Dict[str, str]:
        """Map ORM event → dict for pre-filling the edit form."""
        return {
            "title": event.title or "",
            "date": event.date.isoformat() if event.date else "",
            "location": event.location or "",
            "category": event.category or "",
            "description": event.description or "",
            "status": event.status or DEFAULT_STATUS,
        }

    @staticmethod
    def group_by_status(events) -> dict:
        from models.event_status import STATUS_KEYS

        grouped = {key: [] for key in STATUS_KEYS}
        for event in events:
            key = event.status if event.status in grouped else DEFAULT_STATUS
            grouped[key].append(event)
        return grouped

    @staticmethod
    def update_status(event: Event, status: str) -> Tuple[bool, str]:
        if not is_valid_status(status):
            return False, "Statut invalide."
        event.status = status
        db.session.commit()
        return True, STATUS_LABELS[status]

    @staticmethod
    def update_from_form(
        event: Event,
        data: Dict[str, Any],
    ) -> Tuple[Optional[Event], Dict[str, str], Dict[str, str]]:
        """
        Validate form data, update an existing event, and persist.

        Returns:
            (event, errors, form_data)
        """
        form_data = EventValidator.normalize_form_data(data)
        errors = EventValidator.validate_edit_event(data)

        if errors:
            return None, errors, form_data

        EventFactory.apply_update(event, data)
        db.session.commit()
        return event, {}, form_data

    @staticmethod
    def delete(event: Event) -> str:
        """
        Remove an event from the database.

        Returns:
            The event title (for flash messages).
        """
        title = event.title
        db.session.delete(event)
        db.session.commit()
        return title
