from datetime import date

from src.application.meal_plan.dto import MealPlanRemainingDTO
from src.domain.user.aggregates import DAILY_LIMIT
from src.domain.user.exceptions import SessionNotFound, UserNotFound
from src.domain.user.repositories import UserRepository


class MealPlanRemainingUseCase:
    """Get remaining daily meal plan generations for the current user."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, session_token: str | None) -> MealPlanRemainingDTO:
        """Return how many generations the user has left today."""
        if session_token is None:
            raise SessionNotFound()

        user = await self.user_repository.get_by_session_token(session_token)
        if not user:
            raise UserNotFound()

        if user.is_premium or user.is_admin or user.last_request_date != date.today():
            remaining = DAILY_LIMIT
        else:
            remaining = max(0, DAILY_LIMIT - user.daily_requests)

        return MealPlanRemainingDTO(remaining=remaining, daily_limit=DAILY_LIMIT)
