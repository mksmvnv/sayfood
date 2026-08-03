from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from src.application.meal_plan import (
    MealPlanGenerationUseCase,
    MealPlanHistoryUseCase,
    MealPlanRemainingUseCase,
)
from src.infrastructure.config.settings import settings
from src.interfaces.api.dependencies import (
    get_meal_plan_generation_use_case,
    get_meal_plan_history_use_case,
    get_meal_plan_remaining_use_case,
)
from src.interfaces.api.schemas.meal_plan import (
    MealPlanGenerationRequest,
    MealPlanGenerationResponse,
    MealPlanHistoryItemResponse,
    MealPlanRemainingResponse,
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
        gender=meal_plan_schema.gender,
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


@router.get("/history", response_model=list[MealPlanHistoryItemResponse])
async def get_meal_plan_history(
    request: Request,
    meal_plan_history_use_case: Annotated[
        MealPlanHistoryUseCase, Depends(get_meal_plan_history_use_case)
    ],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[MealPlanHistoryItemResponse]:
    """Get meal plan history for the current user."""
    session_token = request.cookies.get(settings.cookie.name)
    items = await meal_plan_history_use_case.execute(session_token=session_token, limit=limit)

    return [
        MealPlanHistoryItemResponse(
            id=item.id,
            goal=item.goal,
            weight=item.weight,
            height=item.height,
            plan=item.plan,
            created_at=item.created_at,
        )
        for item in items
    ]


@router.get("/remaining", response_model=MealPlanRemainingResponse)
async def get_remaining_requests(
    request: Request,
    meal_plan_remaining_use_case: Annotated[
        MealPlanRemainingUseCase, Depends(get_meal_plan_remaining_use_case)
    ],
) -> MealPlanRemainingResponse:
    """Get remaining daily meal plan generations."""
    session_token = request.cookies.get(settings.cookie.name)
    dto = await meal_plan_remaining_use_case.execute(session_token=session_token)

    return MealPlanRemainingResponse(
        remaining=dto.remaining,
        daily_limit=dto.daily_limit,
    )
