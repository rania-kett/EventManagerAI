"""
test_delete_event.py — Delete Event route tests.
"""

from models import db
from models.event import Event


def test_delete_event_success(client, app, sample_event):
    response = client.post(
        f"/events/{sample_event}/delete",
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "supprimé avec succès" in html
    assert "Salon Tech" in html

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
    assert f"/events/{sample_event}/delete" in html
    assert "delete-event-form" in html
    assert "deleteEventConfirmModal" in html
    assert "deleteEventConfirmBtn" in html
