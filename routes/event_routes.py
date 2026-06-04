"""
routes/event_routes.py — HTTP endpoints for Event CRUD and AI helpers.

Blueprint prefix: /events (registered in app.py).

Planned routes (stubs only in this skeleton):
  GET  /              → list events (index)
  GET  /add           → add form
  POST /add           → create event
  GET  /<id>/edit     → edit form
  POST /<id>/edit     → update event
  POST /<id>/delete   → delete event
  POST /<id>/generate-description → Gemini via ai_service
"""

from flask import Blueprint, render_template

# from models.event import Event
# from models import db
# from factories.event_factory import EventFactory
# from services.ai_service import AIService

event_bp = Blueprint("events", __name__, url_prefix="/events")


@event_bp.route("/")
def index():
    """List all events — implementation pending."""
    # events = Event.query.order_by(Event.date.desc()).all()
    return render_template("index.html", events=[])


@event_bp.route("/add", methods=["GET", "POST"])
def add_event():
    """Show add form (GET) or create event (POST) — implementation pending."""
    return render_template("add_event.html")


@event_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id: int):
    """Show edit form (GET) or update event (POST) — implementation pending."""
    # event = Event.query.get_or_404(event_id)
    return render_template("edit_event.html", event=None, event_id=event_id)


@event_bp.route("/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id: int):
    """Delete event — implementation pending."""
    # TODO: delete + flash + redirect
    return "", 501  # Not Implemented


@event_bp.route("/<int:event_id>/generate-description", methods=["POST"])
def generate_description(event_id: int):
    """Call Gemini to generate/update description — implementation pending."""
    # TODO: AIService.generate_event_description(...)
    return "", 501  # Not Implemented
