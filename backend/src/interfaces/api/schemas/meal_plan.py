from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MealPlanGenerationRequest(BaseModel):
    """Meal plan generation request schema."""

    goal: str
    weight: float = Field(gt=0)
    height: float = Field(gt=0)
    age: int = Field(ge=1, le=120)
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
