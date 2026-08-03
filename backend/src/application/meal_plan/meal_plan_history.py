from src.application.meal_plan.dto import MealPlanHistoryItemDTO
from src.domain.meal_plan.repositories import MealPlanRepository
from src.domain.user.exceptions import SessionNotFound, UserNotFound
from src.domain.user.repositories import UserRepository


class MealPlanHistoryUseCase:
    """Get meal plan history for the current user."""

    def __init__(
        self,
        user_repository: UserRepository,
        meal_plan_repository: MealPlanRepository,
    ):
        self.user_repository = user_repository
        self.meal_plan_repository = meal_plan_repository

    async def execute(
        self,
        session_token: str | None,
        limit: int = 10,
    ) -> list[MealPlanHistoryItemDTO]:
        """Return recent meal plans for the authenticated user."""
        if session_token is None:
            raise SessionNotFound()

        user = await self.user_repository.get_by_session_token(session_token)
        if not user:
            raise UserNotFound()

        meal_plans = await self.meal_plan_repository.get_by_user_id(user.id, limit=limit)

        return [
            MealPlanHistoryItemDTO(
                id=meal_plan.id,
                goal=meal_plan.goal.to_raw(),
                weight=meal_plan.health_params.weight,
                height=meal_plan.health_params.height,
                plan=meal_plan.plan,
                created_at=meal_plan.created_at,
            )
            for meal_plan in meal_plans
        ]
