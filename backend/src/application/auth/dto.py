from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserDTO:
    """User DTO."""

    id: UUID
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime


@dataclass
class UserRegisterDTO:
    """User register DTO."""

    user: UserDTO
    session_token: str
