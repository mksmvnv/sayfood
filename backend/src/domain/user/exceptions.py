from dataclasses import dataclass

from src.domain.seedwork.exceptions import DomainException


# Value object exceptions
@dataclass(eq=False, frozen=True)
class InvalidEmail(DomainException):
    """Raised when email is invalid."""

    code: str = "invalid_email"
    detail: str = "Invalid email"


@dataclass(eq=False, frozen=True)
class InvalidHashedPassword(DomainException):
    """Raised when hashed password is invalid."""

    code: str = "invalid_hashed_password"
    detail: str = "Invalid hashed password"


# Aggregate exceptions


@dataclass(eq=False, frozen=True)
class UserAlreadyActivated(DomainException):
    """Raised when user is already activated."""

    code: str = "user_already_activated"
    detail: str = "User is already activated"


@dataclass(eq=False, frozen=True)
class UserAlreadyDeactivated(DomainException):
    """Raised when user is already deactivated."""

    code: str = "user_already_deactivated"
    detail: str = "User is already deactivated"


@dataclass(eq=False, frozen=True)
class UserAlreadyPromoted(DomainException):
    """Raised when user is already promoted."""

    code: str = "user_already_promoted"
    detail: str = "User is already promoted"


@dataclass(eq=False, frozen=True)
class UserAlreadyDemoted(DomainException):
    """Raised when user is already demoted."""

    code: str = "user_already_demoted"
    detail: str = "User is already demoted"


@dataclass(eq=False, frozen=True)
class SessionAlreadyExists(DomainException):
    """Raised when session already exists."""

    code: str = "session_already_exists"
    detail: str = "Session already exists"


@dataclass(eq=False, frozen=True)
class SessionNotFound(DomainException):
    """Raised when session not found."""

    code: str = "session_not_found"
    detail: str = "Session not found"


@dataclass(eq=False, frozen=True)
class EmailAlreadySame(DomainException):
    """Raised when new email is the same as current email."""

    code: str = "email_already_same"
    detail: str = "New email is the same as current email"


# Infastructure exceptions
@dataclass(eq=False, frozen=True)
class UserNotFound(DomainException):
    """Raised when user not found."""

    code: str = "user_not_found"
    detail: str = "User not found"


@dataclass(eq=False, frozen=True)
class EmailAlreadyExists(DomainException):
    """Raised when email already exists."""

    code: str = "email_already_exists"
    detail: str = "Email already exists"
