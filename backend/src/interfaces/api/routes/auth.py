from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src.application.auth import (
    UserChangeEmailUseCase,
    UserChangePasswordUseCase,
    UserLoginUseCase,
    UserLogoutUseCase,
    UserRegisterUseCase,
)
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import (
    get_user_change_email_use_case,
    get_user_change_password_use_case,
    get_user_login_use_case,
    get_user_logout_use_case,
    get_user_register_use_case,
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
