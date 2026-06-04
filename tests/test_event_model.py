"""
test_event_model.py — Event ORM model tests.
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


def test_event_columns(app):
    with app.app_context():
        columns = {c["name"] for c in db.inspect(db.engine).get_columns("events")}
        assert "status" in {c["name"] for c in db.inspect(db.engine).get_columns("events")}


def test_event_create_and_persist(app):
    with app.app_context():
        event = Event.create(
            title="Tech Meetup",
            event_date=date(2026, 6, 15),
            location="Paris",
            category="Conference",
            description="Annual gathering.",
        )
        db.session.add(event)
        db.session.commit()

        loaded = db.session.get(Event, event.id)
        assert loaded.title == "Tech Meetup"
        assert loaded.date == date(2026, 6, 15)
        assert loaded.location == "Paris"
        assert loaded.category == "Conference"
        assert loaded.description == "Annual gathering."


def test_event_to_dict(app):
    with app.app_context():
        event = Event.create(
            title="Workshop",
            event_date=date(2026, 1, 1),
            category="Training",
        )
        db.session.add(event)
        db.session.commit()

        assert event.to_dict()["date"] == "2026-01-01"
        assert event.to_dict()["category"] == "Training"


def test_event_factory_from_form(app):
    from factories.event_factory import EventFactory

    with app.app_context():
        event = EventFactory.from_form(
            {
                "title": " Hackathon ",
                "date": "2026-12-01",
                "location": "Lyon",
                "category": "Competition",
                "description": "48h build.",
            }
        )
        assert event.title == "Hackathon"
        assert event.date == date(2026, 12, 1)
        assert event.category == "Competition"
