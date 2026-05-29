from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from src.infrastructure.config.settings import settings

url = URL.create(
    drivername=f"{settings.db.driver}+{settings.db.dialect}",
    username=settings.db.user,
    password=settings.db.password.get_secret_value(),
    host=settings.db.host,
    port=settings.db.port,
    database=settings.db.name,
)
async_engine = create_async_engine(url=url)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """Get async session."""
    async with async_session_maker() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    """Base model."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
