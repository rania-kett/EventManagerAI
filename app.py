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

from flask import Flask, render_template

from config import apply_env_to_app, config_by_name
from models import db
from models.db_schema import ensure_database_schema
from models.event import Event  # noqa: F401 — register model with metadata
from routes.event_routes import event_bp
from routes.landing_routes import landing_bp


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
    apply_env_to_app(app)

    # Ensure instance/ exists for SQLite file (config.SQLALCHEMY_DATABASE_URI)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        ensure_database_schema()

    app.register_blueprint(landing_bp)
    app.register_blueprint(event_bp)

    @app.context_processor
    def inject_template_globals():
        from config import is_gemini_configured

        return {"ai_configured": is_gemini_configured(app)}

    @app.before_request
    def refresh_env_from_dotenv():
        """Re-read .env on each request in development (after editing the file)."""
        if app.debug:
            apply_env_to_app(app)

    @app.route("/")
    def home():
        """Page d'accueil premium EventManager AI."""
        return render_template("landing.html")

    return app



# Module-level app for `flask --app app run` and python app.py
app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
