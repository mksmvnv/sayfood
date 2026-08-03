from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from src.application.meal_plan.meal_plan_generation import MealPlanGenerationUseCase
from src.application.meal_plan.meal_plan_history import MealPlanHistoryUseCase
from src.application.meal_plan.meal_plan_remaining import MealPlanRemainingUseCase
from src.domain.user.aggregates import DAILY_LIMIT
from src.domain.user.exceptions import (
    DailyLimitReached,
    SessionNotFound,
    UserInactive,
    UserNotFound,
)
from tests.conftest import (
    FakeMealPlanRepository,
    FakeUserRepository,
    add_session,
    make_meal_plan,
    make_user,
)


@pytest.mark.asyncio
@patch(
    "src.application.meal_plan.meal_plan_generation.generate_meal_plan",
    new_callable=AsyncMock,
    return_value="Generated plan",
)
async def test_meal_plan_generation_success(mock_generate: AsyncMock) -> None:
    user_repo = FakeUserRepository()
    meal_repo = FakeMealPlanRepository()
    user = make_user()
    add_session(user, "gen-token")
    await user_repo.add(user)
    use_case = MealPlanGenerationUseCase(user_repo, meal_repo)

    result = await use_case.execute(
        session_token="gen-token",
        goal="lose_weight",
        weight=80,
        height=180,
        age=30,
        gender="male",
        activity_level="medium",
        allergies=["milk"],
        restrictions=["vegan"],
    )

    assert result.plan == "Generated plan"
    assert len(meal_repo.plans) == 1
    mock_generate.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "src.application.meal_plan.meal_plan_generation.generate_meal_plan",
    new_callable=AsyncMock,
    return_value="Generated plan",
)
async def test_meal_plan_generation_without_optional_lists(mock_generate: AsyncMock) -> None:
    user_repo = FakeUserRepository()
    meal_repo = FakeMealPlanRepository()
    user = make_user()
    add_session(user, "plain-token")
    await user_repo.add(user)
    use_case = MealPlanGenerationUseCase(user_repo, meal_repo)

    result = await use_case.execute(
        session_token="plain-token",
        goal="maintain",
        weight=70,
        height=170,
        age=25,
        gender="female",
        activity_level="low",
        allergies=None,
        restrictions=None,
    )

    assert result.plan == "Generated plan"


@pytest.mark.asyncio
async def test_meal_plan_generation_guards() -> None:
    user_repo = FakeUserRepository()
    meal_repo = FakeMealPlanRepository()
    use_case = MealPlanGenerationUseCase(user_repo, meal_repo)

    with pytest.raises(SessionNotFound):
        await use_case.execute(
            session_token=None,
            goal="lose_weight",
            weight=80,
            height=180,
            age=30,
            gender="male",
            activity_level="medium",
        )

    with pytest.raises(UserNotFound):
        await use_case.execute(
            session_token="missing",
            goal="lose_weight",
            weight=80,
            height=180,
            age=30,
            gender="male",
            activity_level="medium",
        )

    inactive = make_user(is_active=False)
    add_session(inactive, "inactive-token")
    await user_repo.add(inactive)
    with pytest.raises(UserInactive):
        await use_case.execute(
            session_token="inactive-token",
            goal="lose_weight",
            weight=80,
            height=180,
            age=30,
            gender="male",
            activity_level="medium",
        )

    limited = make_user(daily_requests=DAILY_LIMIT, last_request_date=date.today())
    add_session(limited, "limited-token")
    await user_repo.add(limited)
    with pytest.raises(DailyLimitReached):
        await use_case.execute(
            session_token="limited-token",
            goal="lose_weight",
            weight=80,
            height=180,
            age=30,
            gender="male",
            activity_level="medium",
        )


@pytest.mark.asyncio
async def test_meal_plan_history() -> None:
    user_repo = FakeUserRepository()
    meal_repo = FakeMealPlanRepository()
    user = make_user()
    add_session(user, "history-token")
    await user_repo.add(user)
    plan = make_meal_plan(user.id)
    await meal_repo.add(plan)
    use_case = MealPlanHistoryUseCase(user_repo, meal_repo)

    items = await use_case.execute("history-token", limit=5)
    assert len(items) == 1
    assert items[0].goal == "lose_weight"

    with pytest.raises(SessionNotFound):
        await use_case.execute(None)

    with pytest.raises(UserNotFound):
        await use_case.execute("missing")


@pytest.mark.asyncio
async def test_meal_plan_remaining(monkeypatch: pytest.MonkeyPatch) -> None:
    user_repo = FakeUserRepository()
    use_case = MealPlanRemainingUseCase(user_repo)

    with pytest.raises(SessionNotFound):
        await use_case.execute(None)

    with pytest.raises(UserNotFound):
        await use_case.execute("missing")

    today = date(2026, 8, 3)
    monkeypatch.setattr(
        "src.application.meal_plan.meal_plan_remaining.date",
        type("D", (), {"today": staticmethod(lambda: today)}),
    )

    user = make_user(daily_requests=1, last_request_date=today)
    add_session(user, "remaining-token")
    await user_repo.add(user)

    result = await use_case.execute("remaining-token")
    assert result.remaining == DAILY_LIMIT - 1
    assert result.daily_limit == DAILY_LIMIT

    user.last_request_date = date(2026, 8, 2)
    await user_repo.update(user)
    result_new_day = await use_case.execute("remaining-token")
    assert result_new_day.remaining == DAILY_LIMIT

    user.is_premium = True
    user.last_request_date = today
    user.daily_requests = DAILY_LIMIT
    await user_repo.update(user)
    result_premium = await use_case.execute("remaining-token")
    assert result_premium.remaining == DAILY_LIMIT

    user.is_premium = False
    user.is_admin = True
    await user_repo.update(user)
    result_admin = await use_case.execute("remaining-token")
    assert result_admin.remaining == DAILY_LIMIT
