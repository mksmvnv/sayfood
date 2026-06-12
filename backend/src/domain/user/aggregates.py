from dataclasses import dataclass
from typing import Self

from src.domain.seedwork.aggregates import AggregateRoot
from src.domain.user.events import (
    UserCreated,
    UserDeleted,
    UserEmailChanged,
    UserIsActiveChanged,
    UserIsAdminChanged,
    UserPasswordChanged,
)
from src.domain.user.value_objects import Email, HashedPassword


@dataclass(eq=False, kw_only=True)
class User(AggregateRoot):
    """User aggregate."""

    email: Email
    hashed_password: HashedPassword
    is_active: bool = True
    is_admin: bool = False

    @classmethod
    def create(cls, email: Email, hashed_password: HashedPassword) -> Self:
        """Create user."""
        user = cls(email=email, hashed_password=hashed_password)

        user.register_event(
            UserCreated(
                user_id=user.id,
                email=user.email,
            )
        )

        return user

    def activate(self) -> None:
        """Activate user."""
        if self.is_active:
            return None
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
            return None
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
            return None
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
            return None
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
