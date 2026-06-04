"""
routes/event_routes.py — HTTP endpoints for Event CRUD and AI helpers.

Blueprint prefix: /events (registered in app.py).
"""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from models.event import Event
from models.event_status import DEFAULT_STATUS, EVENT_STATUSES
from services.event_service import EventService

event_bp = Blueprint("events", __name__, url_prefix="/events")


def _status_choices():
    return [{"key": key, "label": label} for key, label, _ in EVENT_STATUSES]


@event_bp.route("/")
def index():
    """Kanban board — events grouped by status."""
    events = Event.query.order_by(Event.date.desc(), Event.id.desc()).all()
    status_columns = [
        {"key": key, "label": label}
        for key, label, _ in EVENT_STATUSES
    ]
    return render_template(
        "index.html",
        events_by_status=EventService.group_by_status(events),
        status_columns=status_columns,
    )


@event_bp.route("/<int:event_id>/status", methods=["PATCH", "POST"])
def update_status(event_id: int):
    """Update event status (drag & drop on Kanban board)."""
    event = Event.query.get_or_404(event_id)
    payload = request.get_json(silent=True) or {}
    status = (payload.get("status") or request.form.get("status") or "").strip()

    ok, message = EventService.update_status(event, status)
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    return jsonify(
        {
            "success": True,
            "id": event.id,
            "status": event.status,
            "status_label": message,
        }
    )


@event_bp.route("/add", methods=["GET", "POST"])
def add_event():
    """Show add form (GET) or create event (POST)."""
    errors = {}
    form_data = {
        "title": "",
        "date": "",
        "location": "",
        "category": "",
        "description": "",
        "status": DEFAULT_STATUS,
    }

    if request.method == "POST":
        event, errors, form_data = EventService.create_from_form(request.form)

        if event:
            flash(
                f'Événement « {event.title} » créé avec succès.',
                "success",
            )
            return redirect(url_for("events.index"))

    return render_template(
        "add_event.html",
        errors=errors,
        form=form_data,
        status_choices=_status_choices(),
    )


@event_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id: int):
    """Show edit form (GET) or update event (POST)."""
    event = Event.query.get_or_404(event_id)
    errors = {}
    form_data = EventService.event_to_form(event)

    if request.method == "POST":
        updated, errors, form_data = EventService.update_from_form(
            event, request.form
        )

        if updated:
            flash(
                f'Événement « {updated.title} » mis à jour avec succès.',
                "success",
            )
            return redirect(url_for("events.index"))

    return render_template(
        "edit_event.html",
        event=event,
        event_id=event_id,
        errors=errors,
        form=form_data,
        status_choices=_status_choices(),
    )


@event_bp.route("/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id: int):
    """Delete event from database."""
    event = Event.query.get_or_404(event_id)
    title = EventService.delete(event)
    flash(f'Événement « {title} » supprimé avec succès.', "success")
    return redirect(url_for("events.index"))


@event_bp.route("/<int:event_id>/generate-description", methods=["POST"])
def generate_description(event_id: int):
    """Call Gemini to generate/update description — implementation pending."""
    return "", 501  # Not Implemented
