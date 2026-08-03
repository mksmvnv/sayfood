from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import aiohttp
import pytest

from src.domain.meal_plan.exceptions import MealPlanGenerationError, MealPlanNotFound
from src.domain.meal_plan.value_objects import Goal
from src.domain.user.exceptions import UserNotFound
from src.domain.user.value_objects import Email
from src.infrastructure.auth.hasher import PasswordHasher
from src.infrastructure.auth.session import generate_session_token
from src.infrastructure.database.mappers.meal_plan import meal_plan_to_domain, meal_plan_to_model
from src.infrastructure.database.mappers.user import user_to_domain, user_to_model
from src.infrastructure.database.models import MealPlanModel
from src.infrastructure.database.repositories.meal_plan import SQLAlchemyMealPlanRepository
from src.infrastructure.database.repositories.user import SQLAlchemyUserRepository
from src.infrastructure.llm.prompt import MEAL_PLAN_PROMPT_TEMPLATE
from src.infrastructure.llm.provider import generate_meal_plan
from tests.conftest import make_health_params, make_meal_plan, make_user


def test_password_hasher_round_trip() -> None:
    hasher = PasswordHasher()
    hashed = hasher.hash("password123")

    assert hasher.verify("password123", hashed) is True
    assert hasher.verify("wrongpass1", hashed) is False


def test_generate_session_token_unique() -> None:
    first = generate_session_token()
    second = generate_session_token()

    assert first
    assert second
    assert first != second


def test_user_mapper_round_trip() -> None:
    user = make_user()
    user.daily_requests = 2
    model = user_to_model(user)

    assert model.email == "user@example.com"
    assert model.daily_requests == 2

    restored = user_to_domain(model)
    assert restored.email == user.email
    assert restored.daily_requests == 2


def test_user_mapper_with_sessions(user_model, session_model) -> None:
    restored = user_to_domain(user_model, [session_model])
    assert len(restored.sessions) == 1
    assert restored.sessions[0].token == "active-session"


def test_meal_plan_mapper_round_trip(meal_plan_model) -> None:
    domain = meal_plan_to_domain(meal_plan_model)
    assert domain.health_params.allergies is not None
    assert domain.health_params.restrictions is not None

    model = meal_plan_to_model(domain)
    assert model.allergies == "milk,eggs"
    assert model.restrictions == "vegetarian"


def test_meal_plan_prompt_template() -> None:
    formatted = MEAL_PLAN_PROMPT_TEMPLATE.format(
        goal="lose_weight",
        weight=80,
        height=180,
        age=30,
        activity_level="medium",
        allergies="None",
        restrictions="None",
    )
    assert "lose_weight" in formatted


def test_meal_plan_mapper_without_lists(user_model) -> None:
    now = datetime.now(UTC)
    model = MealPlanModel(
        id=uuid4(),
        user_id=user_model.id,
        goal="maintain",
        weight=70,
        height=170,
        age=25,
        gender="female",
        activity_level="low",
        allergies=None,
        restrictions=None,
        plan="Simple plan",
        created_at=now,
        updated_at=now,
    )
    domain = meal_plan_to_domain(model)
    assert domain.health_params.allergies is None
    assert domain.health_params.restrictions is None

    remapped = meal_plan_to_model(domain)
    assert remapped.allergies is None
    assert remapped.restrictions is None


@pytest.fixture
def sqlite_utc_now(monkeypatch: pytest.MonkeyPatch) -> None:
    """SQLite returns naive datetimes; align repo expiry checks in tests."""
    monkeypatch.setattr(
        "src.infrastructure.database.repositories.user.utc_now",
        lambda: datetime.now(),
    )


@pytest.mark.asyncio
async def test_user_repository_crud(
    db_session, password_hasher: PasswordHasher, sqlite_utc_now: None
) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    plain = "password123"
    user = make_user(hashed_password=password_hasher.hash(plain).to_raw(), email="repo@example.com")
    user.add_session("db-session", datetime.now() + timedelta(days=1))
    user.pull_events()

    await repo.add(user)
    await repo.update(user)

    by_email = await repo.get_by_email(Email("repo@example.com"))
    assert by_email is not None

    by_id = await repo.get_by_id(user.id)
    assert by_id is not None

    by_token = await repo.get_by_session_token("db-session")
    assert by_token is not None

    user.email = Email("updated@example.com")
    await repo.update(user)
    updated = await repo.get_by_id(user.id)
    assert updated is not None
    assert updated.email.to_raw() == "updated@example.com"

    await repo.delete(user.id)
    assert await repo.get_by_id(user.id) is None

    with pytest.raises(UserNotFound):
        await repo.delete(user.id)


@pytest.mark.asyncio
async def test_user_repository_delete_missing_user(db_session) -> None:
    repo = SQLAlchemyUserRepository(db_session)

    with pytest.raises(UserNotFound):
        await repo.delete(uuid4())


@pytest.mark.asyncio
async def test_user_repository_update_and_delete_paths(
    db_session, user_model, session_model, sqlite_utc_now: None
) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    db_session.add(user_model)
    db_session.add(session_model)
    await db_session.commit()

    loaded = await repo.get_by_session_token(session_model.token)
    assert loaded is not None

    loaded.email = Email("patched@example.com")
    await repo.update(loaded)

    with pytest.raises(UserNotFound):
        await repo.update(make_user(email="ghost@example.com"))

    await repo.delete(user_model.id)
    assert await repo.get_by_id(user_model.id) is None


@pytest.mark.asyncio
async def test_user_repository_orphan_session(
    db_session, user_model, session_model, sqlite_utc_now: None
) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    db_session.add(session_model)
    await db_session.commit()

    assert await repo.get_by_session_token(session_model.token) is None


@pytest.mark.asyncio
async def test_user_repository_missing_and_expired(
    db_session, user_model, session_model, sqlite_utc_now: None
) -> None:
    repo = SQLAlchemyUserRepository(db_session)

    assert await repo.get_by_id(user_model.id) is None
    assert await repo.get_by_email(Email("missing@example.com")) is None
    assert await repo.get_by_session_token("missing") is None

    db_session.add(user_model)
    expired = session_model
    expired.expires_at = datetime.now() - timedelta(days=1)
    db_session.add(expired)
    await db_session.commit()

    assert await repo.get_by_session_token(expired.token) is None


@pytest.mark.asyncio
async def test_meal_plan_repository_crud(db_session, user_model) -> None:
    db_session.add(user_model)
    await db_session.commit()

    repo = SQLAlchemyMealPlanRepository(db_session)
    meal_plan = make_meal_plan(user_model.id)
    await repo.add(meal_plan)

    by_id = await repo.get_by_id(meal_plan.id)
    assert by_id is not None

    items = await repo.get_by_user_id(user_model.id, limit=1)
    assert len(items) == 1

    all_items = await repo.get_by_user_id(user_model.id)
    assert len(all_items) == 1

    await repo.delete(meal_plan.id)
    assert await repo.get_by_id(meal_plan.id) is None

    with pytest.raises(MealPlanNotFound):
        await repo.delete(meal_plan.id)


@pytest.mark.asyncio
async def test_generate_meal_plan_success() -> None:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(
        return_value={"choices": [{"message": {"content": "  Plan content  "}}]}
    )
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.post = MagicMock(return_value=response)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)

    with patch("src.infrastructure.llm.provider.aiohttp.ClientSession", return_value=session):
        result = await generate_meal_plan(Goal("maintain"), make_health_params())

    assert result == "  Plan content  "


@pytest.mark.asyncio
async def test_generate_meal_plan_errors() -> None:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value={"choices": []})
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.post = MagicMock(return_value=response)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("src.infrastructure.llm.provider.aiohttp.ClientSession", return_value=session),
        pytest.raises(MealPlanGenerationError),
    ):
        await generate_meal_plan(
            Goal("maintain"),
            make_health_params(allergies=None, restrictions=None),
        )

    failing_response = MagicMock()
    failing_response.raise_for_status = MagicMock(side_effect=aiohttp.ClientError("boom"))
    failing_response.__aenter__ = AsyncMock(return_value=failing_response)
    failing_response.__aexit__ = AsyncMock(return_value=False)
    session.post = MagicMock(return_value=failing_response)

    with (
        patch("src.infrastructure.llm.provider.aiohttp.ClientSession", return_value=session),
        pytest.raises(MealPlanGenerationError),
    ):
        await generate_meal_plan(Goal("maintain"), make_health_params())
