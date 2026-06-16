from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.auth.user_register import UserRegisterUseCase
from src.infrastructure.auth.hasher import PasswordHasher
from src.infrastructure.database.base import get_async_session
from src.infrastructure.database.repositories.user import SQLAlchemyUserRepository


async def get_user_register_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRegisterUseCase:
    """Get user register use case."""
    user_repository = SQLAlchemyUserRepository(session)
    password_hasher = PasswordHasher()
    return UserRegisterUseCase(user_repository, password_hasher)
