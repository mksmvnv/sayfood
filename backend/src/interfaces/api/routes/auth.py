from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src.application.auth import (
    UserChangeEmailUseCase,
    UserChangePasswordUseCase,
    UserLoginUseCase,
    UserLogoutUseCase,
    UserRegisterUseCase,
)
from src.domain.user.exceptions import SessionNotFound, UserNotFound
from src.domain.user.repositories import UserRepository
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import (
    get_user_change_email_use_case,
    get_user_change_password_use_case,
    get_user_login_use_case,
    get_user_logout_use_case,
    get_user_register_use_case,
    get_user_repository,
)
from src.interfaces.api.schemas.auth import (
    UserChangeEmailRequest,
    UserChangeEmailResponse,
    UserChangePasswordRequest,
    UserChangePasswordResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
        samesite=settings.cookie.samesite,
        secure=settings.cookie.secure,
    )
    return UserLoginResponse(
        id=user_login_dto.id,
        email=user_login_dto.email.to_raw(),
        status="logged in",
        session_token=user_login_dto.session_token,
    )


@router.post("/logout", response_model=UserLogoutResponse)
async def logout(
    user_logout_use_case: Annotated[UserLogoutUseCase, Depends(get_user_logout_use_case)],
    request: Request,
    response: Response,
) -> UserLogoutResponse:
    """Logout user."""
    session_name = settings.cookie.name
    session_token = request.cookies.get(session_name)
    await user_logout_use_case.execute(session_token)
    response.delete_cookie(session_name)
    return UserLogoutResponse()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserResponse:
    """Get current user."""
    session_name = settings.cookie.name
    session_token = request.cookies.get(session_name)
    if not session_token:
        raise SessionNotFound()

    user = await user_repository.get_by_session_token(session_token)
    if not user:
        raise UserNotFound()

    return UserResponse(
        id=user.id,
        email=user.email.to_raw(),
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_premium=user.is_premium,
        daily_requests=user.daily_requests,
        last_request_date=user.last_request_date,
        created_at=user.created_at,
    )


@router.post("/me/password", response_model=UserChangePasswordResponse)
async def change_password(
    user_change_password_schema: UserChangePasswordRequest,
    user_change_password_use_case: Annotated[
        UserChangePasswordUseCase, Depends(get_user_change_password_use_case)
    ],
    request: Request,
    response: Response,
) -> UserChangePasswordResponse:
    """Change user password."""
    session_name = settings.cookie.name
    session_token = request.cookies.get(session_name)
    await user_change_password_use_case.execute(
        session_token,
        user_change_password_schema.old_password,
        user_change_password_schema.new_password,
    )
    response.delete_cookie(session_name)
    return UserChangePasswordResponse()


@router.post("/me/email", response_model=UserChangeEmailResponse)
async def change_email(
    user_change_email_schema: UserChangeEmailRequest,
    user_change_email_use_case: Annotated[
        UserChangeEmailUseCase, Depends(get_user_change_email_use_case)
    ],
    request: Request,
    response: Response,
) -> UserChangeEmailResponse:
    """Change user email."""
    session_name = settings.cookie.name
    session_token = request.cookies.get(session_name)
    await user_change_email_use_case.execute(
        session_token,
        user_change_email_schema.old_email,
        user_change_email_schema.new_email,
    )
    response.delete_cookie(session_name)
    return UserChangeEmailResponse()
