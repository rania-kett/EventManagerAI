"""
conftest.py — Shared pytest fixtures for EventManagerAI.
"""

from datetime import date

import pytest

from models import db
from models.event import Event


@pytest.fixture
def app():
    from app import create_app

    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_event(app):
    """Single event in the database."""
    with app.app_context():
        event = Event.create(
            title="Salon Tech",
            event_date=date(2026, 3, 10),
            location="Casablanca",
            category="Salon",
            description="Rencontre professionnelle.",
            status="planned",
        )
        db.session.add(event)
        db.session.commit()
        return event.id


@pytest.fixture
def sample_events(app):
    """Two events with different Kanban statuses."""
    with app.app_context():
        draft_event = Event.create(
            title="Draft Gala",
            event_date=date(2026, 1, 1),
            location="Paris",
            category="Gala",
            description="Draft event.",
            status="draft",
        )
        confirmed_event = Event.create(
            title="Confirmed Summit",
            event_date=date(2026, 2, 1),
            location="Lyon",
            category="Summit",
            description="Confirmed.",
            status="confirmed",
        )
        db.session.add_all([draft_event, confirmed_event])
        db.session.commit()
        return draft_event.id, confirmed_event.id


def valid_event_payload(**overrides):
    """Default valid form payload for create/update tests."""
    payload = {
        "title": "Summer Festival",
        "date": "2026-07-20",
        "location": "Marseille",
        "category": "Festival",
        "description": "Outdoor music and food.",
        "status": "planned",
    }
    payload.update(overrides)
    return payload
