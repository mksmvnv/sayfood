from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.domain.meal_plan.aggregates import MealPlanAggregate


@dataclass
class MealPlanRepository(ABC):
    """Abstract meal plan repository."""

    @abstractmethod
    async def add(self, meal_plan: MealPlanAggregate) -> None:
        """Add new meal plan."""
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, meal_plan_id: UUID) -> MealPlanAggregate | None:
        """Get meal plan by ID."""
        raise NotImplementedError()

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, limit: int | None = None
    ) -> list[MealPlanAggregate]:
        """Get list of meal plans by user ID."""
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, meal_plan_id: UUID) -> None:
        """Delete meal plan."""
        raise NotImplementedError()
