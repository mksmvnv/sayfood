from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from src.domain.seedwork.aggregates import AggregateRoot
from src.domain.user.entities import SessionEntity
from src.domain.user.events import (
    UserAllSessionsRevoked,
    UserCreated,
    UserDeleted,
    UserEmailChanged,
    UserIsActiveChanged,
    UserIsAdminChanged,
    UserPasswordChanged,
    UserSessionCreated,
    UserSessionRevoked,
)
from src.domain.user.exceptions import (
    EmailAlreadySame,
    SessionAlreadyExists,
    SessionNotFound,
    UserAlreadyActivated,
    UserAlreadyDeactivated,
    UserAlreadyDemoted,
    UserAlreadyPromoted,
)
from src.domain.user.value_objects import Email, HashedPassword


@dataclass(eq=False, kw_only=True)
class UserAggregate(AggregateRoot):
    """User aggregate."""

    email: Email
    hashed_password: HashedPassword
    is_active: bool = True
    is_admin: bool = False
    _sessions: list[SessionEntity] = field(default_factory=list, init=False)

    @classmethod
    def create(cls, email: Email, hashed_password: HashedPassword) -> Self:
        """Create user."""
        user = cls(
            email=email,
            hashed_password=hashed_password,
        )

        user.register_event(
            UserCreated(
                user_id=user.id,
                email=user.email,
            )
        )

        return user

    @property
    def sessions(self) -> list[SessionEntity]:
        """Return a copy of user sessions."""
        return self._sessions.copy()

    def activate(self) -> None:
        """Activate user."""
        if self.is_active:
            raise UserAlreadyActivated()
        self.is_active = True
        self.register_event(
            UserIsActiveChanged(
                user_id=self.id,
                is_active=self.is_active,
            )
        )
        self._touch()

    def deactivate(self) -> None:
        """Deactivate user."""
        if not self.is_active:
            raise UserAlreadyDeactivated()
        self.is_active = False
        self.register_event(
            UserIsActiveChanged(
                user_id=self.id,
                is_active=self.is_active,
            )
        )
        self._touch()

    def promote_to_admin(self) -> None:
        """Promote user to admin."""
        if self.is_admin:
            raise UserAlreadyPromoted()
        self.is_admin = True
        self.register_event(
            UserIsAdminChanged(
                user_id=self.id,
                is_admin=self.is_admin,
            )
        )
        self._touch()

    def demote_from_admin(self) -> None:
        """Demote user from admin."""
        if not self.is_admin:
            raise UserAlreadyDemoted()
        self.is_admin = False
        self.register_event(
            UserIsAdminChanged(
                user_id=self.id,
                is_admin=self.is_admin,
            )
        )
        self._touch()

    def change_password(self, hashed_password: HashedPassword) -> None:
        """Change user password.."""
        self.hashed_password = hashed_password
        self.register_event(
            UserPasswordChanged(
                user_id=self.id,
            )
        )
        self._touch()

    def change_email(self, email: Email) -> None:
        """Change user email."""
        if self.email == email:
            raise EmailAlreadySame()
        self.email = email
        self.register_event(
            UserEmailChanged(
                user_id=self.id,
                email=self.email,
            )
        )
        self._touch()

    def delete(self) -> None:
        """Delete user."""
        self.register_event(
            UserDeleted(
                user_id=self.id,
                email=self.email,
            )
        )

    def add_session(self, token: str, expires_at: datetime) -> None:
        """Add user session."""
        if any(session.token == token for session in self._sessions):
            raise SessionAlreadyExists()
        self._sessions.append(
            SessionEntity(
                token=token,
                expires_at=expires_at,
            )
        )
        self.register_event(
            UserSessionCreated(
                user_id=self.id,
            )
        )
        self._touch()

    def revoke_session(self, token: str) -> None:
        """Revoke a specific user session."""
        for session in self._sessions:
            if session.token == token:
                self._sessions.remove(session)
                self.register_event(
                    UserSessionRevoked(
                        user_id=self.id,
                    )
                )
                self._touch()
                return
        raise SessionNotFound

    def revoke_all_sessions(self) -> None:
        """Revoke all user sessions."""
        self._sessions.clear()
        self.register_event(
            UserAllSessionsRevoked(
                user_id=self.id,
            )
        )
        self._touch()
