"""
validators package — Input validation (no Flask or DB dependencies).

Returns field-level error messages for forms before persistence.
"""

from validators.event_validator import EventValidator

__all__ = ["EventValidator"]
