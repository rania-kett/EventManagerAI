"""
factories/event_factory.py — Construct Event models from input data.
"""

from typing import Any, Dict, Optional

from models.event import Event
from models.event_status import DEFAULT_STATUS, is_valid_status
from utils.dates import parse_event_date


class EventFactory:
    """Builds or updates Event ORM instances from plain dictionaries."""

    @staticmethod
    def from_form(form_data: Dict[str, Any]) -> Event:
        """Create a new Event from request form data."""
        return Event.create(
            title=form_data.get("title", ""),
            event_date=parse_event_date(form_data.get("date")),
            location=form_data.get("location"),
            category=form_data.get("category"),
            description=form_data.get("description"),
            status=form_data.get("status") or DEFAULT_STATUS,
        )

    @staticmethod
    def apply_update(event: Event, form_data: Dict[str, Any]) -> Event:
        """Mutate an existing Event from edit form data."""
        event.title = (form_data.get("title") or "").strip()
        event.date = parse_event_date(form_data.get("date"))
        event.location = EventFactory._optional_stripped(form_data.get("location"))
        event.category = EventFactory._optional_stripped(form_data.get("category"))
        event.description = EventFactory._optional_stripped(
            form_data.get("description")
        )
        EventFactory._apply_status(event, form_data.get("status"))
        return event

    @staticmethod
    def _optional_stripped(value: Any) -> Optional[str]:
        stripped = (value or "").strip()
        return stripped or None

    @staticmethod
    def _apply_status(event: Event, raw_status: Any) -> None:
        status = (raw_status or "").strip()
        if status and is_valid_status(status):
            event.status = status
