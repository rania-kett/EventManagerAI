"""test_kanban.py — Kanban board tests."""

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


def test_kanban_renders(client, app):
    with app.app_context():
        e = Event.create(title="Test", event_date=date(2026, 6, 1), location="X", category="Y", description="Z", status="draft")
        db.session.add(e)
        db.session.commit()
    r = client.get("/events/")
    html = r.data.decode("utf-8")
    assert r.status_code == 200
    assert "kanban-board" in html
    assert "Tableau Kanban" in html
