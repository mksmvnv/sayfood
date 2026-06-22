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


class UserChangePasswordRequest(BaseModel):
    """User change password request schema."""

    old_password: str = Field(min_length=8, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class UserChangePasswordResponse(BaseModel):
    """User change password response schema."""

    status: str = "password_was_changed"


class UserChangeEmailRequest(BaseModel):
    """User change email request schema."""

    old_email: EmailStr
    new_email: EmailStr


class UserChangeEmailResponse(BaseModel):
    """User change email response schema."""

    status: str = "email_was_changed"
