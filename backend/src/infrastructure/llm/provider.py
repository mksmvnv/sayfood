import aiohttp

from src.domain.meal_plan.exceptions import MealPlanGenerationError
from src.domain.meal_plan.value_objects import Goal, HealthParams
from src.infrastructure.config.settings import settings
from src.infrastructure.llm.prompt import MEAL_PLAN_PROMPT_TEMPLATE


async def generate_meal_plan(goal: Goal, health_params: HealthParams) -> str:
    """Generate meal plan using OpenRouter API."""
    prompt = MEAL_PLAN_PROMPT_TEMPLATE.format(
        goal=goal.to_raw(),
        weight=health_params.weight,
        height=health_params.height,
        age=health_params.age,
        activity_level=health_params.activity_level.value,
        allergies=", ".join(health_params.allergies) if health_params.allergies else "None",
        restrictions=", ".join(health_params.restrictions)
        if health_params.restrictions
        else "None",
    )

    content = None

    async with (
        aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.llm.timeout)) as session,
        session.post(
            url=settings.llm.url,
            headers={
                "Authorization": f"Bearer {settings.llm.api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm.model,
                "messages": [{"role": "user", "content": prompt}],
            },
        ) as response,
    ):
        response.raise_for_status()
        data = await response.json()

        if data.get("choices") and data["choices"][0].get("message", {}).get("content"):
            content = data["choices"][0]["message"]["content"]

    if content:
        return str(content)

    raise MealPlanGenerationError()
