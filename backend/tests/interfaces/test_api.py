from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from src.application.auth.dto import (
    UserChangeEmailDTO,
    UserChangePasswordDTO,
    UserLoginDTO,
    UserLogoutDTO,
    UserRegisterDTO,
)
from src.application.auth.user_change_email import UserChangeEmailUseCase
from src.application.auth.user_change_password import UserChangePasswordUseCase
from src.application.auth.user_login import UserLoginUseCase
from src.application.auth.user_logout import UserLogoutUseCase
from src.application.auth.user_register import UserRegisterUseCase
from src.application.meal_plan.dto import (
    MealPlanGenerationDTO,
    MealPlanHistoryItemDTO,
    MealPlanRemainingDTO,
)
from src.application.meal_plan.meal_plan_generation import MealPlanGenerationUseCase
from src.application.meal_plan.meal_plan_history import MealPlanHistoryUseCase
from src.application.meal_plan.meal_plan_remaining import MealPlanRemainingUseCase
from src.domain.seedwork.exceptions import InvalidDomainEvent
from src.domain.user.exceptions import SessionNotFound
from src.domain.user.value_objects import Email
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.database.base import get_async_session
from src.interfaces.api.dependencies import (
    get_meal_plan_generation_use_case,
    get_meal_plan_history_use_case,
    get_meal_plan_remaining_use_case,
    get_user_change_email_use_case,
    get_user_change_password_use_case,
    get_user_login_use_case,
    get_user_logout_use_case,
    get_user_register_use_case,
    get_user_repository,
)
from src.interfaces.api.exception_handlers import EXCEPTION_STATUS_MAP, auth_exception_handler
from src.shared.loaders import yaml_loader
from src.shared.time_utils import utc_now
from tests.conftest import make_user


@pytest.fixture
def api_client() -> AsyncClient:
    from src.app import app

    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_dependencies_wiring(db_session) -> None:
    assert isinstance(await get_user_repository(db_session), object)
    assert isinstance(await get_user_register_use_case(db_session), UserRegisterUseCase)
    assert isinstance(await get_user_login_use_case(db_session), UserLoginUseCase)
    assert isinstance(await get_user_logout_use_case(db_session), UserLogoutUseCase)
    assert isinstance(
        await get_user_change_password_use_case(db_session),
        UserChangePasswordUseCase,
    )
    assert isinstance(await get_user_change_email_use_case(db_session), UserChangeEmailUseCase)
    assert isinstance(
        await get_meal_plan_generation_use_case(db_session),
        MealPlanGenerationUseCase,
    )
    assert isinstance(await get_meal_plan_history_use_case(db_session), MealPlanHistoryUseCase)
    assert isinstance(await get_meal_plan_remaining_use_case(db_session), MealPlanRemainingUseCase)


@pytest.mark.asyncio
async def test_get_async_session(db_session) -> None:
    with patch("src.infrastructure.database.base.async_session_maker") as maker:
        maker.return_value.__aenter__ = AsyncMock(return_value=db_session)
        maker.return_value.__aexit__ = AsyncMock(return_value=False)

        generator = get_async_session()
        session = await generator.__anext__()
        assert session is db_session

        with pytest.raises(StopAsyncIteration):
            await generator.__anext__()


def test_yaml_loader(tmp_path: Path) -> None:
    file_path = tmp_path / "settings.yaml"
    file_path.write_text("app:\n  title: Test\n", encoding="utf-8")

    loaded = yaml_loader(file_path)
    assert loaded["app"]["title"] == "Test"

    empty_path = tmp_path / "empty.yaml"
    empty_path.write_text("", encoding="utf-8")
    assert yaml_loader(empty_path) == {}

    with pytest.raises(FileNotFoundError):
        yaml_loader(tmp_path / "missing.yaml")


def test_get_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "app": {"title": "Test API", "cors_origins": ["http://localhost:3000"]},
        "cookie": {"name": "sf_session_id", "httponly": True, "max_age": 100},
        "db": {
            "url": "postgresql+asyncpg://u:p@localhost/db",
            "driver": "postgresql",
            "dialect": "asyncpg",
            "user": "u",
            "password": "p",
            "host": "localhost",
            "port": 5432,
            "name": "db",
        },
        "llm": {
            "url": "https://example.com",
            "api_key": "key",
            "model": "model",
            "timeout": 10,
        },
    }
    monkeypatch.setattr("src.infrastructure.config.settings.yaml_loader", lambda path: payload)

    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app.title == "Test API"


def test_utc_now() -> None:
    now = utc_now()
    assert now.tzinfo is UTC


@pytest.mark.asyncio
async def test_exception_handler_direct() -> None:
    app = FastAPI()
    auth_exception_handler(app)
    handler = app.exception_handlers[Exception]
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})

    for exc_cls, status in EXCEPTION_STATUS_MAP.items():
        response = await handler(request, exc_cls())
        assert response.status_code == status

    domain_response = await handler(request, SessionNotFound())
    assert domain_response.status_code == 401

    unmapped_response = await handler(request, InvalidDomainEvent())
    assert unmapped_response.status_code == 400

    internal_response = await handler(request, RuntimeError("boom"))
    assert internal_response.status_code == 500
    assert internal_response.body


@pytest.mark.asyncio
async def test_auth_routes(api_client: AsyncClient) -> None:
    from src.app import app
    from src.interfaces.api.dependencies import (
        get_user_change_email_use_case,
        get_user_change_password_use_case,
        get_user_login_use_case,
        get_user_logout_use_case,
        get_user_register_use_case,
        get_user_repository,
    )

    user = make_user()
    user_id = user.id

    class FakeRegisterUseCase:
        async def execute(self, email: str, password: str) -> UserRegisterDTO:
            return UserRegisterDTO(id=user_id, email=Email(email))

    class FakeLoginUseCase:
        async def execute(self, email: str, password: str) -> UserLoginDTO:
            return UserLoginDTO(id=user_id, email=Email(email), session_token="login-token")

    class FakeLogoutUseCase:
        async def execute(self, session_token: str | None) -> UserLogoutDTO:
            return UserLogoutDTO()

    class FakeChangePasswordUseCase:
        async def execute(
            self, session_token: str | None, old_password: str, new_password: str
        ) -> UserChangePasswordDTO:
            return UserChangePasswordDTO()

    class FakeChangeEmailUseCase:
        async def execute(
            self, session_token: str | None, old_email: str, new_email: str
        ) -> UserChangeEmailDTO:
            return UserChangeEmailDTO()

    class FakeUserRepository:
        async def get_by_session_token(self, session_token: str):
            return user

    app.dependency_overrides[get_user_register_use_case] = lambda: FakeRegisterUseCase()
    app.dependency_overrides[get_user_login_use_case] = lambda: FakeLoginUseCase()
    app.dependency_overrides[get_user_logout_use_case] = lambda: FakeLogoutUseCase()
    app.dependency_overrides[get_user_change_password_use_case] = (
        lambda: FakeChangePasswordUseCase()
    )
    app.dependency_overrides[get_user_change_email_use_case] = lambda: FakeChangeEmailUseCase()
    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository()

    register = await api_client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert register.status_code == 200

    login = await api_client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert "sf_session_id" in login.cookies

    me = await api_client.get("/auth/me", cookies=login.cookies)
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"

    logout = await api_client.post("/auth/logout", cookies=login.cookies)
    assert logout.status_code == 200

    change_password = await api_client.post(
        "/auth/me/password",
        json={"old_password": "password123", "new_password": "newpassword1"},
        cookies=login.cookies,
    )
    assert change_password.status_code == 200

    change_email = await api_client.post(
        "/auth/me/email",
        json={"old_email": "user@example.com", "new_email": "new@example.com"},
        cookies=login.cookies,
    )
    assert change_email.status_code == 200

    app.dependency_overrides.clear()


def test_auth_me_missing_cookie() -> None:
    from src.app import app

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_auth_me_user_not_found() -> None:
    from src.app import app
    from src.interfaces.api.dependencies import get_user_repository

    class EmptyRepo:
        async def get_by_session_token(self, session_token: str):
            return None

    app.dependency_overrides[get_user_repository] = lambda: EmptyRepo()
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/auth/me", cookies={"sf_session_id": "missing"})
    assert response.status_code == 404
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_meal_plan_routes(api_client: AsyncClient) -> None:
    from src.app import app
    from src.interfaces.api.dependencies import (
        get_meal_plan_generation_use_case,
        get_meal_plan_history_use_case,
        get_meal_plan_remaining_use_case,
    )

    now = datetime.now(UTC)
    plan_id = uuid4()
    user_id = uuid4()

    class FakeGenerationUseCase:
        async def execute(self, **kwargs) -> MealPlanGenerationDTO:
            return MealPlanGenerationDTO(
                id=plan_id,
                user_id=user_id,
                goal="lose_weight",
                plan="Plan",
                created_at=now,
            )

    class FakeHistoryUseCase:
        async def execute(self, session_token: str | None, limit: int = 10):
            return [
                MealPlanHistoryItemDTO(
                    id=plan_id,
                    goal="lose_weight",
                    weight=80,
                    height=180,
                    plan="Plan",
                    created_at=now,
                )
            ]

    class FakeRemainingUseCase:
        async def execute(self, session_token: str | None) -> MealPlanRemainingDTO:
            return MealPlanRemainingDTO(remaining=2, daily_limit=3)

    app.dependency_overrides[get_meal_plan_generation_use_case] = lambda: FakeGenerationUseCase()
    app.dependency_overrides[get_meal_plan_history_use_case] = lambda: FakeHistoryUseCase()
    app.dependency_overrides[get_meal_plan_remaining_use_case] = lambda: FakeRemainingUseCase()

    cookies = {"sf_session_id": "token"}

    generate = await api_client.post(
        "/meal_plan/generate",
        json={
            "goal": "lose_weight",
            "weight": 80,
            "height": 180,
            "age": 30,
            "gender": "male",
            "activity_level": "medium",
        },
        cookies=cookies,
    )
    assert generate.status_code == 200

    history = await api_client.get("/meal_plan/history?limit=5", cookies=cookies)
    assert history.status_code == 200
    assert len(history.json()) == 1

    remaining = await api_client.get("/meal_plan/remaining", cookies=cookies)
    assert remaining.status_code == 200
    assert remaining.json()["remaining"] == 2

    app.dependency_overrides.clear()


def test_app_import() -> None:
    from src.app import app

    assert app.title

    import src.application.auth as auth_pkg
    import src.application.meal_plan as meal_plan_pkg

    assert auth_pkg.UserRegisterUseCase
    assert meal_plan_pkg.MealPlanGenerationUseCase

    import src.infrastructure.config as config_pkg
    import src.infrastructure.database as database_pkg

    assert config_pkg
    assert database_pkg
