from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.aggregates import User as UserAggregate
from src.domain.user.exceptions import UserNotFound
from src.domain.user.repositories import UserRepository
from src.domain.user.value_objects import Email
from src.infrastructure.database.mappers.user_mapper import user_to_domain, user_to_model
from src.infrastructure.database.models import Session as SessionModel
from src.infrastructure.database.models import User as UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_aggregate: UserAggregate) -> None:
        """Add new user."""
        user_model = user_to_model(user_aggregate)
        self._session.add(user_model)

    async def get_by_id(self, user_id: UUID) -> UserAggregate | None:
        """Get user by ID."""
        user_model = await self._session.get(UserModel, user_id)
        if user_model is None:
            return None
        return user_to_domain(user_model)

    async def get_by_email(self, email: Email) -> UserAggregate | None:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == email.to_raw())
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        if user_model is None:
            return None
        return user_to_domain(user_model)

    async def update(self, user_aggregate: UserAggregate) -> None:
        """Update existing user."""
        user_model = await self._session.get(UserModel, user_aggregate.id)
        if user_model is None:
            raise UserNotFound()

        user_model.email = user_aggregate.email.to_raw()
        user_model.hashed_password = user_aggregate.hashed_password.to_raw()
        user_model.is_active = user_aggregate.is_active
        user_model.is_admin = user_aggregate.is_admin

        self._session.add(user_model)

    async def delete(self, user_id: UUID) -> None:
        """Delete user and their sessions."""
        user_model = await self._session.get(UserModel, user_id)
        if user_model is None:
            raise UserNotFound()

        # Delete related session token
        stmt = delete(SessionModel).where(SessionModel.user_id == user_id)
        await self._session.execute(stmt)

        await self._session.delete(user_model)
