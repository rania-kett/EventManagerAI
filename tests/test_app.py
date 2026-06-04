"""
test_app.py — Smoke tests for application factory.

Expand with route, model, factory, and ai_service tests as features land.
"""

import pytest

from app import create_app
from models import db


@pytest.fixture
def app():
    """Flask app configured for testing."""
    application = create_app("testing")
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_app(client):
    """Landing page renders at root."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"EventManager" in response.data
    assert b"intelligence artificielle" in response.data


def test_events_index(client):
    """Event list page renders."""
    response = client.get("/events/")
    assert response.status_code == 200
    assert "Mes événements" in response.data.decode("utf-8")


def test_db_tables_created(app):
    """SQLite in-memory schema includes events table."""
    with app.app_context():
        inspector = db.inspect(db.engine)
        assert "events" in inspector.get_table_names()
