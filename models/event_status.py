"""
models/event_status.py — Kanban status definitions for events.
"""

from typing import Dict, List, Tuple

# (key, display label, CSS modifier)
EVENT_STATUSES: List[Tuple[str, str, str]] = [
    ("draft", "Brouillon", "status-draft"),
    ("planned", "Planifié", "status-planned"),
    ("confirmed", "Confirmé", "status-confirmed"),
    ("in_progress", "En cours", "status-in-progress"),
    ("completed", "Terminé", "status-completed"),
    ("cancelled", "Annulé", "status-cancelled"),
]

STATUS_KEYS: Tuple[str, ...] = tuple(s[0] for s in EVENT_STATUSES)

STATUS_LABELS: Dict[str, str] = {key: label for key, label, _ in EVENT_STATUSES}

DEFAULT_STATUS = "draft"


def is_valid_status(status: str) -> bool:
    return status in STATUS_KEYS
