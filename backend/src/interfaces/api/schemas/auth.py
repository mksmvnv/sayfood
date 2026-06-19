from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User register request schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserRegisterResponse(BaseModel):
    """User register response schema."""

    id: UUID
    email: EmailStr
    status: str = "registered"


class UserLoginRequest(UserRegisterRequest):
    """User login request schema."""

    ...


class UserLoginResponse(UserRegisterResponse):
    """User login response schema."""

    session_token: str


class UserLogoutResponse(BaseModel):
    """User logout response schema."""

    status: str = "logged out"
