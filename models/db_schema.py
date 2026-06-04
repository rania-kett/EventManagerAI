"""
models/db_schema.py — Align SQLite schema with current ORM models.

SQLAlchemy create_all() does not alter existing tables. When models change
during development, this module can recreate tables if configured to do so.
"""

from flask import current_app
from sqlalchemy import inspect

from models import db


def _expected_event_columns():
    from models.event import Event

    return {column.name for column in Event.__table__.columns}


def _actual_event_columns(engine):
    inspector = inspect(engine)
    if "events" not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns("events")}


def ensure_database_schema() -> None:
    """
    Create missing tables; optionally reset when the events schema drifted.

    Controlled by app.config["RESET_DB_ON_SCHEMA_DRIFT"] (development only).
    """
    engine = db.engine
    expected = _expected_event_columns()
    actual = _actual_event_columns(engine)

    if not actual:
        db.create_all()
        return

    if actual == expected:
        return

    if current_app.config.get("RESET_DB_ON_SCHEMA_DRIFT"):
        db.drop_all()
        db.create_all()
        current_app.logger.warning(
            "Database schema was out of date and was recreated "
            "(RESET_DB_ON_SCHEMA_DRIFT=True). Previous event data was removed."
        )
        return

    raise RuntimeError(
        f"Database schema mismatch for 'events'. "
        f"Expected columns {sorted(expected)}, found {sorted(actual)}. "
        "Delete instance/events.db or set RESET_DB_ON_SCHEMA_DRIFT=True in development."
    )
