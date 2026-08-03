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


@dataclass
class MealPlanHistoryItemDTO:
    """Meal plan history item DTO."""

    id: UUID
    goal: str
    weight: float
    height: float
    plan: str
    created_at: datetime


@dataclass
class MealPlanRemainingDTO:
    """Remaining daily generations DTO."""

    remaining: int
    daily_limit: int
