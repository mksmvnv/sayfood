from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.meal_plan.aggregates import MealPlanAggregate
from src.domain.meal_plan.exceptions import MealPlanNotFound
from src.domain.meal_plan.repositories import MealPlanRepository
from src.infrastructure.database.mappers.meal_plan import meal_plan_to_domain, meal_plan_to_model
from src.infrastructure.database.models import MealPlanModel


class SQLAlchemyMealPlanRepository(MealPlanRepository):
    """SQLAlchemy implementation of meal plan repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, meal_plan_aggregate: MealPlanAggregate) -> None:
        """Add new meal plan."""
        meal_plan_model = meal_plan_to_model(meal_plan_aggregate)
        self._session.add(meal_plan_model)
        await self._session.commit()

    async def get_by_id(self, meal_plan_id: UUID) -> MealPlanAggregate | None:
        """Get meal plan by ID."""
        meal_plan_model = await self._session.get(MealPlanModel, meal_plan_id)
        if meal_plan_model is None:
            return None

        return meal_plan_to_domain(meal_plan_model)

    async def get_by_user_id(
        self, user_id: UUID, limit: int | None = None
    ) -> list[MealPlanAggregate]:
        """Get list of meal plans by user ID."""
        meal_plan_stmt = (
            select(MealPlanModel)
            .where(MealPlanModel.user_id == user_id)
            .order_by(MealPlanModel.created_at.desc())
        )
        if limit is not None:
            meal_plan_stmt = meal_plan_stmt.limit(limit)
        meal_plan_result = await self._session.execute(meal_plan_stmt)
        meal_plan_models = meal_plan_result.scalars().all()
        return [meal_plan_to_domain(meal_plan_model) for meal_plan_model in meal_plan_models]

    async def delete(self, meal_plan_id: UUID) -> None:
        """Delete meal plan."""
        meal_plan_model = await self._session.get(MealPlanModel, meal_plan_id)
        if meal_plan_model is None:
            raise MealPlanNotFound()
        await self._session.delete(meal_plan_model)
        await self._session.commit()
