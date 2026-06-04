"""
routes/event_routes.py — HTTP endpoints for Event CRUD and AI helpers.

Blueprint prefix: /events (registered in app.py).
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.event import Event
from services.event_service import EventService

event_bp = Blueprint("events", __name__, url_prefix="/events")


@event_bp.route("/")
def index():
    """List all events, newest first."""
    events = Event.query.order_by(Event.date.desc(), Event.id.desc()).all()
    return render_template("index.html", events=events)


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
    )


@event_bp.route("/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id: int):
    """Delete event — implementation pending."""
    return "", 501  # Not Implemented


@event_bp.route("/<int:event_id>/generate-description", methods=["POST"])
def generate_description(event_id: int):
    """Call Gemini to generate/update description — implementation pending."""
    return "", 501  # Not Implemented
