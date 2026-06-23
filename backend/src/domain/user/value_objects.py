import re
from dataclasses import dataclass

from src.domain.seedwork.value_objects import ValueObject
from src.domain.user.exceptions import InvalidEmail, InvalidHashedPassword


@dataclass(frozen=True)
class Email(ValueObject[str]):
    """Email value object with validation."""

    value: str

    def validate(self) -> None:
        """Validate email."""
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.value):
            raise InvalidEmail()

    def to_raw(self) -> str:
        """Return raw value."""
        return self.value


@dataclass(frozen=True)
class HashedPassword(ValueObject[str]):
    """Hashed password value object."""

    value: str

    def validate(self) -> None:
        """Validate hashed password."""
        if not self.value:
            raise InvalidHashedPassword()

    def to_raw(self) -> str:
        """Return raw value."""
        return self.value
