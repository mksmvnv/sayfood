from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.domain.user.aggregates import User
from src.domain.user.value_objects import Email


@dataclass
class UserRepository(ABC):
    """Abstract user repository."""

    @abstractmethod
    async def add(self, user: User) -> None:
        """Add new user."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> None:
        """Update user."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Delete user."""
        raise NotImplementedError
