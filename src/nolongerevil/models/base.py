"""Base models and utility classes for SQLModel."""

from datetime import datetime

from sqlalchemy import Integer, TypeDecorator


class MillisecondTimestamp(TypeDecorator):
    """Custom SQLAlchemy type for millisecond timestamps.

    Stores datetime as integer milliseconds (JavaScript-style) in the database,
    but exposes as Python datetime in application code.
    """

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> int | None:
        """Convert datetime to millisecond timestamp for database storage."""
        if value is None:
            return None
        return int(value.timestamp() * 1000)

    def process_result_value(self, value: int | None, dialect) -> datetime | None:
        """Convert millisecond timestamp from database to datetime."""
        if value is None:
            return None
        return datetime.fromtimestamp(value / 1000)


def timestamp_to_ms(dt: datetime | None) -> int | None:
    """Convert datetime to millisecond timestamp.

    Args:
        dt: Datetime to convert

    Returns:
        Millisecond timestamp or None
    """
    if dt is None:
        return None
    return int(dt.timestamp() * 1000)


def ms_to_timestamp(ms: int | None) -> datetime | None:
    """Convert millisecond timestamp to datetime.

    Args:
        ms: Millisecond timestamp

    Returns:
        Datetime or None
    """
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000)


def now_ms() -> int:
    """Get current time as millisecond timestamp.

    Returns:
        Current time in milliseconds
    """
    return int(datetime.now().timestamp() * 1000)
