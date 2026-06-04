"""
test_add_event.py — Add Event route and validation tests.
"""

from datetime import date

from models.event import Event
from tests.conftest import valid_event_payload


def test_add_event_get_renders_form(client):
    response = client.get("/events/add")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Créer un événement" in html
    assert "Enregistrer" in html


def test_add_event_post_success(client, app):
    response = client.post(
        "/events/add", data=valid_event_payload(), follow_redirects=True
    )

    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "créé avec succès" in html
    assert "Summer Festival" in html

    with app.app_context():
        event = Event.query.filter_by(title="Summer Festival").one()
        assert event.date == date(2026, 7, 20)
        assert event.location == "Marseille"


def test_add_event_post_empty_title(client, app):
    payload = valid_event_payload(title="   ")

    response = client.post("/events/add", data=payload)
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Titre obligatoire" in html

    with app.app_context():
        assert Event.query.count() == 0


def test_add_event_post_missing_fields(client, app):
    response = client.post(
        "/events/add",
        data={
            "title": "Only Title",
            "date": "",
            "location": "",
            "category": "",
            "description": "",
        },
    )
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "obligatoire" in html

    with app.app_context():
        assert Event.query.count() == 0


def test_add_event_post_invalid_date(client, app):
    payload = valid_event_payload(date="not-a-date")

    response = client.post("/events/add", data=payload)
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Date invalide" in html

    with app.app_context():
        assert Event.query.count() == 0
