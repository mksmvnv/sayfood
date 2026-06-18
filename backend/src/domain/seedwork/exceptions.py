from dataclasses import dataclass


@dataclass(eq=False)
class DomainException(Exception):
    """Base domain exception."""

    code: str = "domain_error"
    detail: str = "Domain error"

    def __str__(self) -> str:
        """Return exception message."""
        return self.detail


@dataclass(eq=False)
class InvalidDomainEvent(DomainException):
    """Raised when provided domain event does not inherit Event."""

    code: str = "invalid_domain_event"
    detail: str = "Domain event must inherit Event"
