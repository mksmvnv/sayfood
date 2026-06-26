from src.domain.meal_plan.aggregates import MealPlanAggregate
from src.domain.meal_plan.value_objects import ActivityLevelType, Goal, HealthParams
from src.infrastructure.database.models import MealPlanModel


def meal_plan_to_model(meal_plan_aggregate: MealPlanAggregate) -> MealPlanModel:
    """Convert domain MealPlan to ORM MealPlanModel."""
    return MealPlanModel(
        id=meal_plan_aggregate.id,
        user_id=meal_plan_aggregate.user_id,
        goal=meal_plan_aggregate.goal.to_raw(),
        weight=meal_plan_aggregate.health_params.weight,
        height=meal_plan_aggregate.health_params.height,
        age=meal_plan_aggregate.health_params.age,
        activity_level=meal_plan_aggregate.health_params.activity_level.value,
        allergies=",".join(meal_plan_aggregate.health_params.allergies)
        if meal_plan_aggregate.health_params.allergies
        else None,
        restrictions=",".join(meal_plan_aggregate.health_params.restrictions)
        if meal_plan_aggregate.health_params.restrictions
        else None,
        plan=meal_plan_aggregate.plan,
        created_at=meal_plan_aggregate.created_at,
        updated_at=meal_plan_aggregate.updated_at,
    )


def meal_plan_to_domain(meal_plan_model: MealPlanModel) -> MealPlanAggregate:
    """Convert ORM MealPlanModel to domain MealPlan."""
    return MealPlanAggregate(
        id=meal_plan_model.id,
        user_id=meal_plan_model.user_id,
        goal=Goal(meal_plan_model.goal),
        health_params=HealthParams(
            weight=meal_plan_model.weight,
            height=meal_plan_model.height,
            age=meal_plan_model.age,
            activity_level=ActivityLevelType(meal_plan_model.activity_level),
            allergies=meal_plan_model.allergies.split(",") if meal_plan_model.allergies else [],
            restrictions=meal_plan_model.restrictions.split(",")
            if meal_plan_model.restrictions
            else [],
        ),
        plan=meal_plan_model.plan,
        created_at=meal_plan_model.created_at,
        updated_at=meal_plan_model.updated_at,
    )
