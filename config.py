"""
config.py — Application configuration.

Centralizes environment-specific settings (development, production, testing).
Keeps secrets out of source code: load GEMINI_API_KEY and SECRET_KEY from
environment variables or a .env file (see .env.example).

Used by app.create_app() via app.config.from_object().
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root (directory containing app.py)
BASE_DIR = Path(__file__).resolve().parent

# Load .env from project root before Config reads environment variables
load_dotenv(BASE_DIR / ".env")

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'events.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Gemini AI — prepared for future integration (services/ai_service.py)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)


class DevelopmentConfig(Config):
    """Local development defaults."""

    DEBUG = True
    # Recreate tables when models change (SQLite has no auto-migrate in this project)
    RESET_DB_ON_SCHEMA_DRIFT = True


class ProductionConfig(Config):
    """Production: debug off, require explicit secrets."""

    DEBUG = False


class TestingConfig(Config):
    """In-memory SQLite for pytest (tests/)."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Map name → class for FLASK_ENV or explicit selection in app.py
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def reload_env() -> None:
    """Reload .env into os.environ (call on app startup)."""
    load_dotenv(BASE_DIR / ".env", override=True)


def apply_env_to_app(app) -> None:
    """
    Push fresh environment variables into Flask app.config.

    Fixes stale Config class values when .env is edited after import.
    """
    reload_env()
    app.config["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "").strip()
    app.config["GEMINI_MODEL"] = (
        os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
        or DEFAULT_GEMINI_MODEL
    )
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", app.config.get("SECRET_KEY", "dev-change-me-in-production")
    )


def is_gemini_configured(app=None) -> bool:
    """True when a non-empty GEMINI_API_KEY is available."""
    if app is not None:
        key = (app.config.get("GEMINI_API_KEY") or "").strip()
        if key:
            return True
    reload_env()
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())
