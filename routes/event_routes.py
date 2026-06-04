"""
routes/event_routes.py — HTTP endpoints for Event CRUD, Kanban, and AI helpers.

Blueprint prefix: /events (registered in app.py).
"""

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from config import is_gemini_configured
from constants.event_form import EMPTY_EVENT_FORM
from routes.ai_handlers import (
    generate_and_save_description_response,
    generate_description_response,
    parse_ai_payload,
)
from services.event_service import EventService
from services.messages import (
    flash_event_created,
    flash_event_deleted,
    flash_event_updated,
)

event_bp = Blueprint("events", __name__, url_prefix="/events")


@event_bp.route("/")
def index():
    """Kanban board — events grouped by status."""
    events = EventService.list_events_ordered()
    return render_template(
        "index.html",
        events_by_status=EventService.group_by_status(events),
        status_columns=EventService.kanban_column_definitions(),
    )


@event_bp.route("/<int:event_id>/status", methods=["PATCH", "POST"])
def update_status(event_id: int):
    """Update event status (drag & drop on Kanban board)."""
    event = EventService.get_event_or_404(event_id)
    payload = request.get_json(silent=True) or {}
    new_status = (payload.get("status") or request.form.get("status") or "").strip()

    success, message = EventService.update_status(event, new_status)
    if not success:
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
    return _handle_event_form(
        template_name="add_event.html",
        page_title="Créer un événement",
        submit_label="Enregistrer l'événement",
        empty_form=EMPTY_EVENT_FORM.copy(),
        save_action=EventService.create_from_form,
        success_flash=flash_event_created,
    )


@event_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id: int):
    """Show edit form (GET) or update event (POST)."""
    event = EventService.get_event_or_404(event_id)
    return _handle_event_form(
        template_name="edit_event.html",
        page_title="Modifier l'événement",
        submit_label="Enregistrer les modifications",
        empty_form=EventService.event_to_form(event),
        save_action=lambda form_data: EventService.update_from_form(event, form_data),
        success_flash=flash_event_updated,
        event=event,
        event_id=event_id,
    )


@event_bp.route("/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id: int):
    """Delete event from database."""
    event = EventService.get_event_or_404(event_id)
    title = EventService.delete(event)
    flash(flash_event_deleted(title), "success")
    return redirect(url_for("events.index"))


@event_bp.route("/ai/generate-description", methods=["POST"])
def ai_generate_description():
    """Generate event description via Gemini (add/edit forms)."""
    body, status_code = generate_description_response(parse_ai_payload(request))
    return jsonify(body), status_code


@event_bp.route("/<int:event_id>/generate-description", methods=["POST"])
def generate_description(event_id: int):
    """Generate description for an existing event and save to database."""
    event = EventService.get_event_or_404(event_id)
    body, status_code = generate_and_save_description_response(event)
    return jsonify(body), status_code


def _handle_event_form(
    *,
    template_name: str,
    page_title: str,
    submit_label: str,
    empty_form: dict,
    save_action,
    success_flash,
    event=None,
    event_id=None,
):
    """Shared GET/POST flow for create and edit forms."""
    errors = {}
    form_data = empty_form

    if request.method == "POST":
        saved_event, errors, form_data = save_action(request.form)
        if saved_event:
            flash(success_flash(saved_event.title), "success")
            return redirect(url_for("events.index"))

    return render_template(
        template_name,
        errors=errors,
        form=form_data,
        status_choices=EventService.kanban_column_definitions(),
        page_title=page_title,
        submit_label=submit_label,
        event=event,
        event_id=event_id,
        ai_configured=is_gemini_configured(current_app),
    )
