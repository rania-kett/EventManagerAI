"""User-facing flash messages for event operations."""


def flash_event_created(title: str) -> str:
    return f"Événement « {title} » créé avec succès."


def flash_event_updated(title: str) -> str:
    return f"Événement « {title} » mis à jour avec succès."


def flash_event_deleted(title: str) -> str:
    return f"Événement « {title} » supprimé avec succès."
