from datetime import datetime
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import Session as SessionModel
from src.shared.time_utils import utc_now


class SQLAlchemySessionRepository:
    """SQLAlchemy implementation of session repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, token: str, user_id: UUID, expires_at: datetime) -> None:
        """Add session token."""
        session = SessionModel(token=token, user_id=user_id, expires_at=expires_at)
        self._session.add(session)

    async def get(self, token: str) -> SessionModel | None:
        """Get session token."""
        return await self._session.get(SessionModel, token)

    async def delete(self, token: str) -> None:
        """Delete session token."""
        session = await self.get(token)
        if session:
            await self._session.delete(session)

    async def delete_expired(self) -> None:
        """Delete expired session token."""
        stmt = delete(SessionModel).where(SessionModel.expires_at < utc_now())
        await self._session.execute(stmt)
