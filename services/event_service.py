"""
services/event_service.py — Event use cases (create, update, delete).
"""

from typing import Any, Dict, Optional, Tuple

from factories.event_factory import EventFactory
from models import db
from models.event import Event
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
