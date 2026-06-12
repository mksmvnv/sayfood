from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.shared.time_utils import utc_now


@dataclass(frozen=True, kw_only=True)
class Event(ABC):
    """Base event."""

    event_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
