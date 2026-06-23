from dataclasses import dataclass, field

from src.domain.seedwork.entities import Entity
from src.domain.seedwork.events import Event
from src.domain.seedwork.exceptions import InvalidDomainEvent


@dataclass(eq=False, kw_only=True)
class AggregateRoot(Entity):
    """Base aggregate root."""

    _events: list[Event] = field(default_factory=list, init=False)

    def register_event(self, event: Event) -> None:
        """Register domain event."""
        if not isinstance(event, Event):
            raise InvalidDomainEvent()
        self._events.append(event)

    def pull_events(self) -> list[Event]:
        """Pull domain events and clear storage."""
        registered_events = self._events.copy()
        self._events.clear()
        return registered_events
