from dataclasses import dataclass

from src.domain.seedwork.exceptions import DomainException


@dataclass(eq=False, frozen=True)
class InvalidEmail(DomainException):
    """Raised when email is invalid."""

    code: str = "invalid_email"
    detail: str = "Invalid Email"


@dataclass(eq=False, frozen=True)
class InvalidHashedPassword(DomainException):
    """Raised when hashed password is invalid."""

    code: str = "invalid_hashed_password"
    detail: str = "Invalid Hashed Password"


@dataclass(eq=False, frozen=True)
class UserNotFound(DomainException):
    """User not found exception."""

    code: str = "user_not_found"
    detail: str = "User not found"
