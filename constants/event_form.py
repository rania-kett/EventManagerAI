"""
event_form.py — Single source of truth for event form field names and labels.
"""

from typing import Dict, Tuple

from models.event_status import DEFAULT_STATUS

EVENT_FORM_FIELDS: Tuple[str, ...] = (
    "title",
    "date",
    "location",
    "category",
    "description",
)

EVENT_FIELD_LABELS: Dict[str, str] = {
    "title": "Titre",
    "date": "Date",
    "location": "Lieu",
    "category": "Catégorie",
    "description": "Description",
    "status": "Statut",
}

EMPTY_EVENT_FORM: Dict[str, str] = {
    field: "" for field in EVENT_FORM_FIELDS
} | {"status": DEFAULT_STATUS}
