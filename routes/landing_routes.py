"""
routes/landing_routes.py — Marketing / landing pages (premium UI).
"""

from typing import Tuple

from flask import Blueprint, flash, redirect, request, url_for

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/contact", methods=["POST"])
def contact():
    """Réception du formulaire de contact (accusé de réception)."""
    name, email, message = _read_contact_fields(request.form)

    if not all((name, email, message)):
        flash("Veuillez remplir tous les champs du formulaire.", "warning")
    else:
        flash(
            f"Merci {name}, votre message a bien été reçu. "
            "Nous vous répondrons sous peu.",
            "success",
        )
    return redirect(url_for("home") + "#contact")


def _read_contact_fields(form) -> Tuple[str, str, str]:
    return (
        (form.get("name") or "").strip(),
        (form.get("email") or "").strip(),
        (form.get("message") or "").strip(),
    )
