from src.application.meal_plan.dto import MealPlanGenerationDTO
from src.domain.meal_plan.aggregates import MealPlanAggregate
from src.domain.meal_plan.repositories import MealPlanRepository
from src.domain.meal_plan.value_objects import (
    ActivityLevelType,
    AllergenType,
    Goal,
    HealthParams,
    RestrictionType,
)
from src.domain.user.exceptions import (
    DailyLimitReached,
    SessionNotFound,
    UserInactive,
    UserNotFound,
)
from src.domain.user.repositories import UserRepository
from src.infrastructure.llm.provider import generate_meal_plan


class MealPlanGenerationUseCase:
    """Meal plan generation Use Case."""

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
        goal: str,
        weight: float,
        height: float,
        age: int,
        activity_level: str,
        allergies: list[str] | None = None,
        restrictions: list[str] | None = None,
    ) -> MealPlanGenerationDTO:
        """Execute meal plan generation."""
        # Check if session exists
        if session_token is None:
            raise SessionNotFound()

        # Check session
        user = await self.user_repository.get_by_session_token(session_token)
        if not user:
            raise UserNotFound()

        if not user.is_active:
            raise UserInactive()

        if not user.can_generate_today():
            raise DailyLimitReached()

        # Convert data type
        allergies_enum = None
        if allergies:
            allergies_enum = [AllergenType(a) for a in allergies]

        restrictions_enum = None
        if restrictions:
            restrictions_enum = [RestrictionType(r) for r in restrictions]

        # Create value objects
        goal_vo = Goal(goal)
        health_params_vo = HealthParams(
            weight=weight,
            height=height,
            age=age,
            activity_level=ActivityLevelType(activity_level),
            allergies=allergies_enum,
            restrictions=restrictions_enum,
        )

        # Generate meal plan
        plan_text = await generate_meal_plan(goal_vo, health_params_vo)

        # Create domain meal plan
        meal_plan = MealPlanAggregate.create(
            user_id=user.id,
            health_params=health_params_vo,
            plan=plan_text,
        )

        # Update request limit
        user.increment_requests()
        await self.user_repository.update(user)

        # Save meal plan to database
        await self.meal_plan_repository.add(meal_plan)

        return MealPlanGenerationDTO(
            id=meal_plan.id,
            user_id=meal_plan.user_id,
            goal=meal_plan.goal.to_raw(),
            plan=meal_plan.plan,
            created_at=meal_plan.created_at,
        )
