"""
test_kanban.py — Kanban board and status update tests.
"""

from models import db
from models.event import Event


def test_kanban_board_renders(client, sample_events):
    response = client.get("/events/")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Tableau Kanban" in html
    assert "kanban-board" in html
    assert "Draft Gala" in html
    assert "Confirmed Summit" in html
    assert "Draft" in html
    assert "Confirmed" in html
    assert "data-drop-zone" in html


def test_update_status_patch(client, app, sample_events):
    draft_id, _ = sample_events

    response = client.patch(
        f"/events/{draft_id}/status",
        json={"status": "in_progress"},
        headers={"Content-Type": "application/json"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["status"] == "in_progress"
    assert data["status_label"] == "In Progress"

    with app.app_context():
        event = db.session.get(Event, draft_id)
        assert event.status == "in_progress"


def test_update_status_invalid(client, sample_events):
    draft_id, _ = sample_events

    response = client.patch(
        f"/events/{draft_id}/status",
        json={"status": "invalid_status"},
    )

    assert response.status_code == 400


def test_new_event_defaults_to_draft(client, app):
    response = client.post(
        "/events/add",
        data={
            "title": "New Board Event",
            "date": "2026-08-01",
            "location": "Nice",
            "category": "Meetup",
            "description": "Kanban default status.",
            "status": "draft",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        event = Event.query.filter_by(title="New Board Event").one()
        assert event.status == "draft"


def test_create_event_with_planned_status(client, app):
    response = client.post(
        "/events/add",
        data={
            "title": "Planned Conference",
            "date": "2026-09-15",
            "location": "Rabat",
            "category": "Conférence",
            "description": "Starts as planned.",
            "status": "planned",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        event = Event.query.filter_by(title="Planned Conference").one()
        assert event.status == "planned"


def test_edit_event_status(client, app, sample_events):
    draft_id, _ = sample_events

    response = client.post(
        f"/events/{draft_id}/edit",
        data={
            "title": "Draft Gala Updated",
            "date": "2026-01-01",
            "location": "Paris",
            "category": "Gala",
            "description": "Now confirmed.",
            "status": "confirmed",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        event = db.session.get(Event, draft_id)
        assert event.status == "confirmed"
        assert event.title == "Draft Gala Updated"
