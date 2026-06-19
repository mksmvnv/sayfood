from dataclasses import dataclass
from uuid import UUID

from src.domain.user.value_objects import Email


@dataclass
class UserRegisterDTO:
    """User register DTO."""

    id: UUID
    email: Email


@dataclass
class UserLoginDTO(UserRegisterDTO):
    """User login DTO."""

    session_token: str


@dataclass
class UserLogoutDTO:
    """User logout DTO."""

    ...
