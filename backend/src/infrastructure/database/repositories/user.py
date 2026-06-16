from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.aggregates import UserAggregate
from src.domain.user.exceptions import UserNotFound
from src.domain.user.repositories import UserRepository
from src.domain.user.value_objects import Email
from src.infrastructure.database.mappers.user import user_to_domain, user_to_model
from src.infrastructure.database.models import SessionModel, UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_aggregate: UserAggregate) -> None:
        """Add new user."""
        user_model = user_to_model(user_aggregate)
        self._session.add(user_model)

        for session in user_aggregate.sessions:
            self._session.add(
                SessionModel(
                    token=session.token,
                    user_id=user_aggregate.id,
                    expires_at=session.expires_at,
                )
            )

    async def get_by_id(self, user_id: UUID) -> UserAggregate | None:
        """Get user by ID."""
        user_model = await self._session.get(UserModel, user_id)
        if user_model is None:
            return None

        session_stmt = select(SessionModel).where(SessionModel.user_id == user_id)
        session_result = await self._session.execute(session_stmt)
        session_models = list(session_result.scalars().all())

        return user_to_domain(user_model, session_models)

    async def get_by_email(self, email: Email) -> UserAggregate | None:
        """Get user by email."""
        user_stmt = select(UserModel).where(UserModel.email == email.to_raw())
        user_result = await self._session.execute(user_stmt)
        user_model = user_result.scalar_one_or_none()

        if user_model is None:
            return None

        session_stmt = select(SessionModel).where(SessionModel.user_id == user_model.id)
        session_result = await self._session.execute(session_stmt)
        session_models = list(session_result.scalars().all())

        return user_to_domain(user_model, session_models)

    async def update(self, user_aggregate: UserAggregate) -> None:
        """Update existing user."""
        user_model = await self._session.get(UserModel, user_aggregate.id)
        if user_model is None:
            raise UserNotFound()

        user_model.email = user_aggregate.email.to_raw()
        user_model.hashed_password = user_aggregate.hashed_password.to_raw()
        user_model.is_active = user_aggregate.is_active
        user_model.is_admin = user_aggregate.is_admin

        # Delete old sessions
        await self._session.execute(
            delete(SessionModel).where(SessionModel.user_id == user_aggregate.id)
        )

        # Save new sessions
        for session in user_aggregate.sessions:
            self._session.add(
                SessionModel(
                    token=session.token,
                    user_id=user_aggregate.id,
                    expires_at=session.expires_at,
                )
            )

    async def delete(self, user_id: UUID) -> None:
        """Delete user and his sessions."""
        session_stmt = delete(SessionModel).where(SessionModel.user_id == user_id)
        await self._session.execute(session_stmt)

        user_model = await self._session.get(UserModel, user_id)
        if user_model is None:
            raise UserNotFound()
        await self._session.delete(user_model)
