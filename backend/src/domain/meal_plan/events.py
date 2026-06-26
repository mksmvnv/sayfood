from dataclasses import dataclass
from uuid import UUID

from src.domain.seedwork.events import Event


@dataclass(frozen=True, kw_only=True)
class MealPlanCreated(Event):
    """Meal plan created event."""

    user_id: UUID
