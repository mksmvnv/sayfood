from dataclasses import dataclass

from src.domain.seedwork.exceptions import DomainException


@dataclass(eq=False)
class InvalidEmail(DomainException):
    """Raised when email is invalid."""

    code: str = "invalid_email"
    detail: str = "Invalid email"


@dataclass(eq=False)
class InvalidHashedPassword(DomainException):
    """Raised when hashed password is invalid."""

    code: str = "invalid_hashed_password"
    detail: str = "Invalid hashed password"


@dataclass(eq=False)
class UserAlreadyActivated(DomainException):
    """Raised when user is already activated."""

    code: str = "user_already_activated"
    detail: str = "User is already activated"


@dataclass(eq=False)
class UserAlreadyDeactivated(DomainException):
    """Raised when user is already deactivated."""

    code: str = "user_already_deactivated"
    detail: str = "User is already deactivated"


@dataclass(eq=False)
class UserAlreadyPromoted(DomainException):
    """Raised when user is already promoted."""

    code: str = "user_already_promoted"
    detail: str = "User is already promoted"


@dataclass(eq=False)
class UserAlreadyDemoted(DomainException):
    """Raised when user is already demoted."""

    code: str = "user_already_demoted"
    detail: str = "User is already demoted"


@dataclass(eq=False)
class SessionAlreadyExists(DomainException):
    """Raised when session already exists."""

    code: str = "session_already_exists"
    detail: str = "Session already exists"


@dataclass(eq=False)
class SessionNotFound(DomainException):
    """Raised when session not found."""

    code: str = "session_not_found"
    detail: str = "Session not found"


@dataclass(eq=False)
class EmailAlreadySame(DomainException):
    """Raised when new email is the same as current email."""

    code: str = "email_already_same"
    detail: str = "New email is the same as current email"


# Infastructure exceptions
@dataclass(eq=False)
class UserNotFound(DomainException):
    """Raised when user not found."""

    code: str = "user_not_found"
    detail: str = "User not found"


@dataclass(eq=False)
class EmailAlreadyExists(DomainException):
    """Raised when email already exists."""

    code: str = "email_already_exists"
    detail: str = "Email already exists"


@dataclass(eq=False)
class InvalidPassword(DomainException):
    """Raised when password is invalid."""

    code: str = "invalid_password"
    detail: str = "Invalid password"
