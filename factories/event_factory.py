"""
factories/event_factory.py — Construct Event models from input data.

Keeps routes free of repetitive field assignment. Use for:
  - Form POST → Event
  - Seed data / tests
  - Partial updates (edit)
"""

from datetime import date, datetime
from typing import Any, Dict, Optional

from models.event import Event


class EventFactory:
    """Builds or updates Event ORM instances from plain dictionaries."""

    @staticmethod
    def from_form(data: Dict[str, Any]) -> Event:
        """
        Create a new Event from request form / JSON body.

        Expected keys: title, date, location, category, description
        """
        return Event.create(
            title=data.get("title", ""),
            event_date=EventFactory._parse_date(data.get("date")),
            location=data.get("location"),
            category=data.get("category"),
            description=data.get("description"),
        )

    @staticmethod
    def apply_update(event: Event, data: Dict[str, Any]) -> Event:
        """Mutate an existing Event from edit form data."""
        parsed_date = EventFactory._parse_date(data.get("date"))
        event.title = data.get("title", "").strip()
        event.date = parsed_date
        event.location = (data.get("location") or "").strip() or None
        event.category = (data.get("category") or "").strip() or None
        event.description = (data.get("description") or "").strip() or None
        return event

    @staticmethod
    def _parse_date(value: Optional[Any]) -> Optional[date]:
        """Parse ISO date (YYYY-MM-DD) or date/datetime objects."""
        if value is None or value == "":
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None
        return None
