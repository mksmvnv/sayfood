from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject[VT](ABC):
    """Abstract base value object."""

    value: VT

    def __post_init__(self) -> None:
        """Validate value object after initialization."""
        object.__setattr__(self, "value", deepcopy(self.value))
        self.validate()

    @abstractmethod
    def validate(self) -> None:
        """Validate value object."""
        raise NotImplementedError

    @abstractmethod
    def to_raw(self) -> VT:
        """Return raw value."""
        raise NotImplementedError
