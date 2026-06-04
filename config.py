"""
config.py — Application configuration.

Centralizes environment-specific settings (development, production, testing).
Keeps secrets out of source code: load GEMINI_API_KEY and SECRET_KEY from
environment variables or a .env file (see .env.example).

Used by app.create_app() via app.config.from_object().
"""

import os
from pathlib import Path


# Project root (directory containing app.py)
BASE_DIR = Path(__file__).resolve().parent


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
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


class DevelopmentConfig(Config):
    """Local development defaults."""

    DEBUG = True


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
