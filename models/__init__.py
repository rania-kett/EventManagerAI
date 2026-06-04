"""
models package — Data layer (persistence).

Holds the SQLAlchemy extension and ORM models. Routes and services should
import models from here, not define schema in controllers.

Event entity: models/event.py
"""

from flask_sqlalchemy import SQLAlchemy

# Shared database handle; initialized in app.create_app()
db = SQLAlchemy()
