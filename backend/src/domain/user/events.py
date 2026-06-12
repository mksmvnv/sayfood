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


@dataclass(frozen=True, kw_only=True)
class UserIsActiveChanged(UserChanged):
    """User active status changed event."""

    is_active: bool


@dataclass(frozen=True, kw_only=True)
class UserIsAdminChanged(UserChanged):
    """User admin status changed event."""

    is_admin: bool


@dataclass(frozen=True, kw_only=True)
class UserPasswordChanged(UserChanged):
    """User password changed event."""

    ...


@dataclass(frozen=True, kw_only=True)
class UserEmailChanged(UserChanged):
    """User email changed event."""

    email: Email


@dataclass(frozen=True, kw_only=True)
class UserDeleted(UserChanged):
    """User deleted event."""

    email: Email
