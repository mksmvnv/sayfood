from dataclasses import dataclass
from typing import Self
from uuid import UUID

from src.domain.meal_plan.events import MealPlanCreated
from src.domain.meal_plan.value_objects import Goal, HealthParams
from src.domain.seedwork.aggregates import AggregateRoot


@dataclass(eq=False, kw_only=True)
class MealPlanAggregate(AggregateRoot):
    """Meal plan aggregate."""

    user_id: UUID
    goal: Goal
    health_params: HealthParams
    plan: str

    @classmethod
    def create(
        cls,
        user_id: UUID,
        goal: Goal,
        health_params: HealthParams,
        plan: str,
    ) -> Self:
        """Create meal plan."""
        meal_plan = cls(
            user_id=user_id,
            goal=goal,
            health_params=health_params,
            plan=plan,
        )
        meal_plan.register_event(MealPlanCreated(user_id=user_id))
        return meal_plan
