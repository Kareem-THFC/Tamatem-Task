"""Helpers for turning model column values into JSON-safe values."""

from datetime import datetime, timezone


def iso_utc(value: datetime | None) -> str | None:
    """Serialise a stored UTC timestamp as an unambiguous ISO-8601 string.
    """
    return None if value is None else value.replace(tzinfo=timezone.utc).isoformat()
