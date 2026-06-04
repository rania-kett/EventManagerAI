"""
test_edit_event.py — Edit Event route and update tests.
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
            title="Salon Tech",
            event_date=date(2026, 3, 10),
            location="Casablanca",
            category="Salon",
            description="Rencontre professionnelle.",
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id
    return event_id


def _updated_payload():
    return {
        "title": "Salon Tech 2026",
        "date": "2026-06-01",
        "location": "Rabat",
        "category": "Conférence",
        "description": "Édition 2026 enrichie par l'IA.",
    }


def test_edit_event_get_prefilled(client, sample_event):
    response = client.get(f"/events/{sample_event}/edit")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Salon Tech" in html
    assert "Casablanca" in html
    assert 'value="2026-03-10"' in html
    assert "Enregistrer les modifications" in html


def test_edit_event_post_success(client, app, sample_event):
    response = client.post(
        f"/events/{sample_event}/edit",
        data=_updated_payload(),
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "mis à jour avec succès" in html
    assert "Salon Tech 2026" in html

    with app.app_context():
        event = db.session.get(Event, sample_event)
        assert event.title == "Salon Tech 2026"
        assert event.date == date(2026, 6, 1)
        assert event.location == "Rabat"
        assert event.category == "Conférence"


def test_edit_event_post_empty_title(client, app, sample_event):
    payload = _updated_payload()
    payload["title"] = "   "

    response = client.post(f"/events/{sample_event}/edit", data=payload)
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Titre obligatoire" in html

    with app.app_context():
        event = db.session.get(Event, sample_event)
        assert event.title == "Salon Tech"


def test_edit_event_not_found(client):
    response = client.get("/events/9999/edit")
    assert response.status_code == 404
