from dataclasses import dataclass
from uuid import UUID

from src.domain.seedwork.events import Event
from src.domain.user.value_objects import Email


@dataclass(frozen=True, kw_only=True)
class UserCreated(Event):
    """User created event."""

    user_id: UUID
    email: Email


@dataclass(frozen=True, kw_only=True)
class UserChanged(Event):
    """User changed event."""

    user_id: UUID
    email: Email


@dataclass(frozen=True, kw_only=True)
class UserIsActiveChanged(UserChanged):
    """User active status changed event."""

    is_active: bool


@dataclass(frozen=True, kw_only=True)
class UserIsAdminChanged(UserChanged):
    """User admin status changed event."""

    is_admin: bool
