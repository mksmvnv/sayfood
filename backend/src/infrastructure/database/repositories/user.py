from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.aggregates import User as UserAggregate
from src.domain.user.exceptions import UserNotFound
from src.domain.user.repositories import UserRepository
from src.domain.user.value_objects import Email, HashedPassword
from src.infrastructure.database.models import User as UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_aggregate: UserAggregate) -> None:
        """Add new user."""
        user_model = self._to_model(user_aggregate)
        self._session.add(user_model)

    async def get_by_id(self, id: UUID) -> UserAggregate | None:
        """Get user by ID."""
        user_model = await self._session.get(UserModel, id)
        if user_model is None:
            return None
        return self._to_domain(user_model)

    async def get_by_email(self, email: Email) -> UserAggregate | None:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == email.to_raw())
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        if user_model is None:
            return None
        return self._to_domain(user_model)

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

    def _to_model(self, user_aggregate: UserAggregate) -> UserModel:
        """Convert domain User to ORM UserModel."""
        return UserModel(
            id=user_aggregate.id,
            email=user_aggregate.email.to_raw(),
            hashed_password=user_aggregate.hashed_password.to_raw(),
            is_active=user_aggregate.is_active,
            is_admin=user_aggregate.is_admin,
            created_at=user_aggregate.created_at,
            updated_at=user_aggregate.updated_at,
        )

    def _to_domain(self, user_model: UserModel) -> UserAggregate:
        """Convert ORM UserModel to domain User."""
        return UserAggregate(
            id=user_model.id,
            email=Email(user_model.email),
            hashed_password=HashedPassword(user_model.hashed_password),
            is_active=user_model.is_active,
            is_admin=user_model.is_admin,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
        )
