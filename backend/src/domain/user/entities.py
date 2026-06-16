from dataclasses import dataclass
from datetime import datetime

from src.domain.seedwork.entities import Entity
from src.shared.time_utils import utc_now


@dataclass(eq=False, kw_only=True)
class SessionEntity(Entity):
    """Session entity."""

    token: str
    expires_at: datetime

    def is_expired(self) -> bool:
        """Check session exists."""
        return self.expires_at < utc_now()
