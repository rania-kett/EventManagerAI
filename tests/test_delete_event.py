"""
test_delete_event.py — Delete Event route tests.
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
    with app.app_context():
        event = Event.create(
            title="Gala de clôture",
            event_date=date(2026, 9, 1),
            location="Tanger",
            category="Gala",
            description="Soirée de fin d'année.",
        )
        db.session.add(event)
        db.session.commit()
        return event.id


def test_delete_event_success(client, app, sample_event):
    response = client.post(
        f"/events/{sample_event}/delete",
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "supprimé avec succès" in html
    assert "Gala de clôture" in html

    with app.app_context():
        assert db.session.get(Event, sample_event) is None


def test_delete_event_not_found(client):
    response = client.post("/events/9999/delete")
    assert response.status_code == 404


def test_delete_button_on_index(client, app, sample_event):
    response = client.get("/events/")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Supprimer" in html
    assert f'/events/{sample_event}/delete' in html
    assert "delete-event-form" in html or "kanban-card" in html
