from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.auth import (
    UserChangeEmailUseCase,
    UserChangePasswordUseCase,
    UserLoginUseCase,
    UserLogoutUseCase,
    UserRegisterUseCase,
)
from src.application.meal_plan import MealPlanGenerationUseCase
from src.infrastructure.auth.hasher import PasswordHasher
from src.infrastructure.database.base import get_async_session
from src.infrastructure.database.repositories import (
    SQLAlchemyMealPlanRepository,
    SQLAlchemyUserRepository,
)


async def get_user_register_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRegisterUseCase:
    """Get user register use case."""
    user_repository = SQLAlchemyUserRepository(session)
    password_hasher = PasswordHasher()
    return UserRegisterUseCase(user_repository, password_hasher)


async def get_user_login_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserLoginUseCase:
    """Get user login use case."""
    user_repository = SQLAlchemyUserRepository(session)
    password_hasher = PasswordHasher()
    return UserLoginUseCase(user_repository, password_hasher)


async def get_user_logout_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserLogoutUseCase:
    """Get user logout use case."""
    user_repository = SQLAlchemyUserRepository(session)
    return UserLogoutUseCase(user_repository)


async def get_user_change_password_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserChangePasswordUseCase:
    """Get user change password use case."""
    user_repository = SQLAlchemyUserRepository(session)
    password_hasher = PasswordHasher()
    return UserChangePasswordUseCase(user_repository, password_hasher)


async def get_user_change_email_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserChangeEmailUseCase:
    """Get user change email use case."""
    user_repository = SQLAlchemyUserRepository(session)
    return UserChangeEmailUseCase(user_repository)


async def get_meal_plan_generation_use_case(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MealPlanGenerationUseCase:
    """Get meal plan generation use case."""
    user_repository = SQLAlchemyUserRepository(session)
    meal_plan_repository = SQLAlchemyMealPlanRepository(session)
    return MealPlanGenerationUseCase(user_repository, meal_plan_repository)
