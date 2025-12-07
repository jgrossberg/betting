from datetime import datetime, timezone
from sqlalchemy import DateTime, TypeDecorator


class TZDateTime(TypeDecorator):
    """A DateTime type that ensures timezone-aware datetimes.

    PostgreSQL returns timezone-aware datetimes natively.
    SQLite returns naive datetimes - this normalizes them to UTC.
    """
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
