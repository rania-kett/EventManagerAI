"""
test_add_event.py — Add Event route and validation tests.
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


def _valid_payload():
    return {
        "title": "Summer Festival",
        "date": "2026-07-20",
        "location": "Marseille",
        "category": "Festival",
        "description": "Outdoor music and food.",
    }


def test_add_event_get_renders_form(client):
    response = client.get("/events/add")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Créer un événement" in html
    assert "Enregistrer" in html


def test_add_event_post_success(client, app):
    response = client.post("/events/add", data=_valid_payload(), follow_redirects=True)

    assert response.status_code == 200
    assert b"was created successfully" in response.data
    assert b"Summer Festival" in response.data

    with app.app_context():
        event = Event.query.filter_by(title="Summer Festival").one()
        assert event.date == date(2026, 7, 20)
        assert event.location == "Marseille"


def test_add_event_post_empty_title(client, app):
    payload = _valid_payload()
    payload["title"] = "   "

    response = client.post("/events/add", data=payload)

    assert response.status_code == 200
    assert b"Title is required" in response.data

    with app.app_context():
        assert Event.query.count() == 0


def test_add_event_post_missing_fields(client, app):
    response = client.post(
        "/events/add",
        data={"title": "Only Title", "date": "", "location": "", "category": "", "description": ""},
    )

    assert response.status_code == 200
    assert b"is required" in response.data

    with app.app_context():
        assert Event.query.count() == 0


def test_add_event_post_invalid_date(client, app):
    payload = _valid_payload()
    payload["date"] = "not-a-date"

    response = client.post("/events/add", data=payload)

    assert response.status_code == 200
    assert b"valid date" in response.data

    with app.app_context():
        assert Event.query.count() == 0
