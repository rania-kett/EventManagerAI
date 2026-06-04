"""
test_app.py — Smoke tests for application factory.
"""

from models import db


def test_create_app(client):
    """Landing page renders at root."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"EventManager" in response.data
    assert b"intelligence artificielle" in response.data


def test_events_index(client):
    """Kanban board page renders."""
    response = client.get("/events/")
    assert response.status_code == 200
    assert "Tableau Kanban" in response.data.decode("utf-8")


def test_db_tables_created(app):
    """SQLite in-memory schema includes events table."""
    with app.app_context():
        inspector = db.inspect(db.engine)
        assert "events" in inspector.get_table_names()
