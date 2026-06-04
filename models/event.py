"""
models/event.py — Event domain entity (SQLAlchemy ORM).

Maps the `events` table. Persistence only — validation and use cases
live in factories/ and services/.
"""

from datetime import date, datetime
from typing import Any, Dict, Optional

from models import db


class Event(db.Model):
    """A scheduled event with optional AI-generated description."""

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    location = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Event {self.id}: {self.title!r} on {self.date}>"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for templates, APIs, and tests."""
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date.isoformat() if self.date else None,
            "location": self.location,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def create(
        cls,
        title: str,
        event_date: date,
        location: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Event":
        """Build an unsaved instance (caller commits via db.session)."""
        return cls(
            title=title.strip(),
            date=event_date,
            location=location.strip() if location else None,
            category=category.strip() if category else None,
            description=description.strip() if description else None,
        )
