from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.shared.time_utils import utc_now


@dataclass(eq=False, kw_only=True)
class Entity(ABC):
    """Base entity."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def _touch(self) -> None:
        """Update last modification timestamp."""
        self.updated_at = utc_now()

    def __eq__(self, other: object) -> bool:
        """Compare entities by id."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash entities by id."""
        return hash(self.id)
