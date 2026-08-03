from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MealPlanGenerationRequest(BaseModel):
    """Meal plan generation request schema."""

    goal: str
    weight: float = Field(gt=0)
    height: float = Field(gt=0)
    age: int = Field(ge=1, le=120)
    gender: str
    activity_level: str
    allergies: list[str] | None = None
    restrictions: list[str] | None = None


class MealPlanGenerationResponse(BaseModel):
    """Meal plan generation response schema."""

    id: UUID
    user_id: UUID
    plan: str
    created_at: datetime
    status: str = "meal_plan_generated"


class MealPlanHistoryItemResponse(BaseModel):
    """Meal plan history item response schema."""

    id: UUID
    goal: str
    weight: float
    height: float
    plan: str
    created_at: datetime


class MealPlanRemainingResponse(BaseModel):
    """Remaining daily generations response schema."""

    remaining: int
    daily_limit: int
