from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MealPlanGenerationDTO:
    """Meal plan generation DTO."""

    id: UUID
    user_id: UUID
    goal: str
    plan: str
    created_at: datetime
