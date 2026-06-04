"""
app.py — Application entry point and factory.

Responsibilities:
  - Create Flask app (application factory pattern)
  - Load config from config.py
  - Initialize SQLAlchemy and database tables
  - Register blueprints (routes/event_routes.py)

Run locally: flask --app app run --debug
Or: python app.py
"""

import os
from pathlib import Path
from typing import Optional

from flask import Flask, redirect, url_for

from config import config_by_name
from models import db
from models.event import Event  # noqa: F401 — register model with metadata
from routes.event_routes import event_bp


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Application factory — preferred for tests and multiple environments.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )

    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Ensure instance/ exists for SQLite file (config.SQLALCHEMY_DATABASE_URI)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(event_bp)

    @app.route("/")
    def home():
        """Root URL redirects to event list."""
        return redirect(url_for("events.index"))

    return app


# Module-level app for `flask --app app run` and python app.py
app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
