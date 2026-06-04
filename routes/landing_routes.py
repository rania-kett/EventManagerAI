"""
routes/landing_routes.py — Marketing / landing pages (premium UI).
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/contact", methods=["POST"])
def contact():
    """Réception du formulaire de contact (accusé de réception)."""
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()

    if not name or not email or not message:
        flash("Veuillez remplir tous les champs du formulaire.", "warning")
    else:
        flash(
            f"Merci {name}, votre message a bien été reçu. Nous vous répondrons sous peu.",
            "success",
        )
    return redirect(url_for("home") + "#contact")
