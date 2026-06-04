"""
dates.py — Parse event dates from forms, APIs, and ORM values.
"""

from datetime import date, datetime
from typing import Any, Optional


def parse_event_date(value: Optional[Any]) -> Optional[date]:
    """Parse ISO date (YYYY-MM-DD) or date/datetime objects."""
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None
