from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.application.auth import UserLoginUseCase, UserRegisterUseCase
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import get_user_login_use_case, get_user_register_use_case
from src.interfaces.api.schemas.auth import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRegisterResponse)
async def register(
    user_register_schema: UserRegisterRequest,
    user_register_use_case: Annotated[UserRegisterUseCase, Depends(get_user_register_use_case)],
) -> UserRegisterResponse:
    """Register user."""
    user_register_dto = await user_register_use_case.execute(
        user_register_schema.email, user_register_schema.password
    )
    return UserRegisterResponse(
        id=user_register_dto.id,
        email=user_register_dto.email.to_raw(),
    )


@router.post("/login", response_model=UserLoginResponse)
async def login(
    user_login_schema: UserLoginRequest,
    user_login_use_case: Annotated[UserLoginUseCase, Depends(get_user_login_use_case)],
    response: Response,
) -> UserLoginResponse:
    """Login user."""
    user_login_dto = await user_login_use_case.execute(
        user_login_schema.email, user_login_schema.password
    )
    response.set_cookie(
        key=settings.cookie.name,
        value=user_login_dto.session_token,
        httponly=settings.cookie.httponly,
        max_age=settings.cookie.max_age,
    )
    return UserLoginResponse(
        id=user_login_dto.id,
        email=user_login_dto.email.to_raw(),
        status="logged in",
        session_token=user_login_dto.session_token,
    )
