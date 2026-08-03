from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.meal_plan.aggregates import MealPlanAggregate
from src.domain.meal_plan.repositories import MealPlanRepository
from src.domain.meal_plan.value_objects import (
    ActivityLevelType,
    GenderType,
    Goal,
    HealthParams,
)
from src.domain.user.aggregates import UserAggregate
from src.domain.user.repositories import UserRepository
from src.domain.user.value_objects import Email, HashedPassword
from src.infrastructure.auth.hasher import PasswordHasher
from src.infrastructure.database.base import BaseModel
from src.infrastructure.database.models import MealPlanModel, SessionModel, UserModel


class FakeUserRepository(UserRepository):
    """In-memory user repository for use case tests."""

    def __init__(self) -> None:
        self.users: dict[UUID, UserAggregate] = {}

    async def add(self, user: UserAggregate) -> None:
        self.users[user.id] = user

    async def get_by_id(self, user_id: UUID) -> UserAggregate | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: Email) -> UserAggregate | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def get_by_session_token(self, session_token: str) -> UserAggregate | None:
        for user in self.users.values():
            for session in user.sessions:
                if session.token == session_token:
                    return user
        return None

    async def update(self, user: UserAggregate) -> None:
        self.users[user.id] = user

    async def delete(self, user_id: UUID) -> None:
        self.users.pop(user_id, None)


class FakeMealPlanRepository(MealPlanRepository):
    """In-memory meal plan repository for use case tests."""

    def __init__(self) -> None:
        self.plans: dict[UUID, MealPlanAggregate] = {}

    async def add(self, meal_plan: MealPlanAggregate) -> None:
        self.plans[meal_plan.id] = meal_plan

    async def get_by_id(self, meal_plan_id: UUID) -> MealPlanAggregate | None:
        return self.plans.get(meal_plan_id)

    async def get_by_user_id(
        self, user_id: UUID, limit: int | None = None
    ) -> list[MealPlanAggregate]:
        items = [plan for plan in self.plans.values() if plan.user_id == user_id]
        items.sort(key=lambda plan: plan.created_at, reverse=True)
        if limit is not None:
            return items[:limit]
        return items

    async def delete(self, meal_plan_id: UUID) -> None:
        self.plans.pop(meal_plan_id, None)


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return PasswordHasher()


@pytest.fixture
def fake_user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_meal_plan_repo() -> FakeMealPlanRepository:
    return FakeMealPlanRepository()


def make_email(value: str = "user@example.com") -> Email:
    return Email(value)


def make_hashed_password(value: str = "$2b$12$hashedpasswordvalue") -> HashedPassword:
    return HashedPassword(value)


def make_user(
    email: str = "user@example.com",
    hashed_password: str = "$2b$12$hashedpasswordvalue",
    *,
    is_active: bool = True,
    is_admin: bool = False,
    is_premium: bool = False,
    daily_requests: int = 0,
    last_request_date: date | None = None,
) -> UserAggregate:
    user = UserAggregate.create(email=Email(email), hashed_password=HashedPassword(hashed_password))
    user.is_active = is_active
    user.is_admin = is_admin
    user.is_premium = is_premium
    user.daily_requests = daily_requests
    user.last_request_date = last_request_date
    user.pull_events()
    return user


def make_health_params(**overrides: Any) -> HealthParams:
    defaults: dict[str, Any] = {
        "weight": 80.0,
        "height": 180.0,
        "age": 30,
        "gender": GenderType.MALE,
        "activity_level": ActivityLevelType.MEDIUM,
        "allergies": None,
        "restrictions": None,
    }
    defaults.update(overrides)
    return HealthParams(**defaults)


def make_meal_plan(user_id: UUID | None = None, plan: str = "Test plan") -> MealPlanAggregate:
    return MealPlanAggregate.create(
        user_id=user_id or uuid4(),
        goal=Goal("lose_weight"),
        health_params=make_health_params(),
        plan=plan,
    )


def add_session(user: UserAggregate, token: str = "session-token") -> None:
    user.add_session(token=token, expires_at=datetime.now(UTC) + timedelta(days=7))
    user.pull_events()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def user_model() -> UserModel:
    now = datetime.now(UTC)
    return UserModel(
        id=uuid4(),
        email="user@example.com",
        hashed_password="hashed",
        daily_requests=0,
        last_request_date=None,
        is_active=True,
        is_admin=False,
        is_premium=False,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def meal_plan_model(user_model: UserModel) -> MealPlanModel:
    now = datetime.now(UTC)
    return MealPlanModel(
        id=uuid4(),
        user_id=user_model.id,
        goal="lose_weight",
        weight=80.0,
        height=180.0,
        age=30,
        gender="male",
        activity_level="medium",
        allergies="milk,eggs",
        restrictions="vegetarian",
        plan="Breakfast: oats",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def session_model(user_model: UserModel) -> SessionModel:
    return SessionModel(
        token="active-session",
        user_id=user_model.id,
        expires_at=datetime.now() + timedelta(days=1),
    )
