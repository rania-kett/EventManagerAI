"""
services/event_service.py — Event use cases (CRUD, Kanban, AI persistence).
"""

from typing import Any, Dict, List, Optional, Tuple

from flask import abort

from factories.event_factory import EventFactory
from models import db
from models.event import Event
from models.event_status import DEFAULT_STATUS, EVENT_STATUSES, STATUS_KEYS, STATUS_LABELS, is_valid_status
from services.ai_service import AIService
from validators.event_validator import EventValidator

FormResult = Tuple[Optional[Event], Dict[str, str], Dict[str, str]]
StatusResult = Tuple[bool, str]


class EventService:
    """Orchestrates validation, factories, and database persistence."""

    @staticmethod
    def list_events_ordered() -> List[Event]:
        """All events, newest by date then id."""
        return Event.query.order_by(Event.date.desc(), Event.id.desc()).all()

    @staticmethod
    def get_event_or_404(event_id: int) -> Event:
        event = db.session.get(Event, event_id)
        if event is None:
            abort(404)
        return event

    @staticmethod
    def kanban_column_definitions() -> List[Dict[str, str]]:
        return [{"key": key, "label": label} for key, label, _ in EVENT_STATUSES]

    @staticmethod
    def group_by_status(events: List[Event]) -> Dict[str, List[Event]]:
        """Group events into Kanban columns keyed by status."""
        columns = {status_key: [] for status_key in STATUS_KEYS}
        for event in events:
            column_key = (
                event.status if event.status in columns else DEFAULT_STATUS
            )
            columns[column_key].append(event)
        return columns

    @staticmethod
    def create_from_form(form_data: Dict[str, Any]) -> FormResult:
        normalized = EventValidator.normalize_form_data(form_data)
        errors = EventValidator.validate(form_data)
        if errors:
            return None, errors, normalized

        new_event = EventFactory.from_form(form_data)
        db.session.add(new_event)
        db.session.commit()
        return new_event, {}, normalized

    @staticmethod
    def update_from_form(event: Event, form_data: Dict[str, Any]) -> FormResult:
        normalized = EventValidator.normalize_form_data(form_data)
        errors = EventValidator.validate(form_data)
        if errors:
            return None, errors, normalized

        EventFactory.apply_update(event, form_data)
        db.session.commit()
        return event, {}, normalized

    @staticmethod
    def event_to_form(event: Event) -> Dict[str, str]:
        """Map ORM event → dict for pre-filling forms."""
        return {
            "title": event.title or "",
            "date": event.date.isoformat() if event.date else "",
            "location": event.location or "",
            "category": event.category or "",
            "description": event.description or "",
            "status": event.status or DEFAULT_STATUS,
        }

    @staticmethod
    def update_status(event: Event, new_status: str) -> StatusResult:
        if not is_valid_status(new_status):
            return False, "Invalid status."

        event.status = new_status
        db.session.commit()
        return True, STATUS_LABELS[new_status]

    @staticmethod
    def delete(event: Event) -> str:
        title = event.title
        db.session.delete(event)
        db.session.commit()
        return title

    @staticmethod
    def save_description(event: Event, description: str) -> None:
        event.description = description.strip()
        db.session.commit()

    @staticmethod
    def generate_description_with_ai(
        ai_service: AIService,
        *,
        title: str,
        location: Optional[str] = None,
        event_date: Optional[Any] = None,
        category: Optional[str] = None,
    ) -> str:
        return ai_service.generate_event_description(
            title=title,
            location=location,
            event_date=event_date,
            category=category,
        )
