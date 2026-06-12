from datetime import UTC, datetime


def utc_now() -> datetime:
    """Get current datetime in UTC."""
    return datetime.now(UTC)
