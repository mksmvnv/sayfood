from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.application.meal_plan.meal_plan_generation import MealPlanGenerationUseCase
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import get_meal_plan_generation_use_case
from src.interfaces.api.schemas.meal_plan import (
    MealPlanGenerationRequest,
    MealPlanGenerationResponse,
)

router = APIRouter(prefix="/meal_plan", tags=["Meal Plan"])


@router.post("/generate", response_model=MealPlanGenerationResponse)
async def generate_meal_plan(
    request: Request,
    meal_plan_schema: MealPlanGenerationRequest,
    meal_plan_generation_use_case: Annotated[
        MealPlanGenerationUseCase, Depends(get_meal_plan_generation_use_case)
    ],
) -> MealPlanGenerationResponse:
    """Generate a meal plan."""
    session_token = request.cookies.get(settings.cookie.name)

    dto = await meal_plan_generation_use_case.execute(
        session_token=session_token,
        goal=meal_plan_schema.goal,
        weight=meal_plan_schema.weight,
        height=meal_plan_schema.height,
        age=meal_plan_schema.age,
        activity_level=meal_plan_schema.activity_level,
        allergies=meal_plan_schema.allergies,
        restrictions=meal_plan_schema.restrictions,
    )

    return MealPlanGenerationResponse(
        id=dto.id,
        user_id=dto.user_id,
        plan=dto.plan,
        created_at=dto.created_at,
    )
