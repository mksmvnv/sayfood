from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.application.auth.dto import UserRegisterDTO
from src.application.auth.user_register import UserRegisterUseCase
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import get_user_register_use_case
from src.interfaces.api.schemas.auth import UserRegisterSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRegisterDTO)
async def register(
    user_register_schema: UserRegisterSchema,
    response: Response,
    user_register_use_case: Annotated[UserRegisterUseCase, Depends(get_user_register_use_case)],
) -> UserRegisterDTO:
    """Register user."""
    user_register_dto = await user_register_use_case.execute(
        user_register_schema.email, user_register_schema.password
    )
    response.set_cookie(
        key=settings.cookie.name,
        value=user_register_dto.session_token,
        httponly=settings.cookie.httponly,
        max_age=settings.cookie.max_age,
    )
    return user_register_dto
