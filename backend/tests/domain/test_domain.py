from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest

from src.domain.meal_plan.aggregates import MealPlanAggregate
from src.domain.meal_plan.events import MealPlanCreated
from src.domain.meal_plan.exceptions import (
    InvalidActivityLevel,
    InvalidAge,
    InvalidAllergen,
    InvalidGoal,
    InvalidHeight,
    InvalidRestriction,
    InvalidWeight,
    MealPlanGenerationError,
    MealPlanNotFound,
)
from src.domain.meal_plan.value_objects import (
    ActivityLevelType,
    AllergenType,
    GenderType,
    Goal,
    HealthParams,
    RestrictionType,
)
from src.domain.seedwork.aggregates import AggregateRoot
from src.domain.seedwork.entities import Entity
from src.domain.seedwork.exceptions import DomainException, InvalidDomainEvent
from src.domain.user.aggregates import DAILY_LIMIT, UserAggregate
from src.domain.user.entities import SessionEntity
from src.domain.user.events import (
    UserAllSessionsRevoked,
    UserCreated,
    UserDeleted,
    UserEmailChanged,
    UserIsActiveChanged,
    UserIsAdminChanged,
    UserPasswordChanged,
    UserSessionCreated,
    UserSessionRevoked,
)
from src.domain.user.exceptions import (
    DailyLimitReached,
    EmailAlreadyExists,
    EmailAlreadySame,
    InvalidCredentials,
    InvalidEmail,
    InvalidHashedPassword,
    PasswordAlreadySame,
    SessionAlreadyExists,
    SessionNotFound,
    UserAlreadyActivated,
    UserAlreadyDeactivated,
    UserAlreadyDemoted,
    UserAlreadyPromoted,
    UserInactive,
    UserNotFound,
)
from src.domain.user.value_objects import Email, HashedPassword
from tests.conftest import make_hashed_password, make_health_params, make_user


class _DummyEntity(Entity):
    pass


class _DummyAggregate(AggregateRoot):
    pass


def test_entity_equality_and_touch() -> None:
    first = _DummyEntity()
    second = _DummyEntity()
    same = _DummyEntity(id=first.id)

    assert first == same
    assert first != second
    assert first != "not-an-entity"
    assert hash(first) == hash(same)

    before = first.updated_at
    first._touch()
    assert first.updated_at >= before


def test_aggregate_events() -> None:
    aggregate = _DummyAggregate()
    event = MealPlanCreated(user_id=uuid4())

    aggregate.register_event(event)
    pulled = aggregate.pull_events()

    assert pulled == [event]
    assert aggregate.pull_events() == []

    with pytest.raises(InvalidDomainEvent):
        aggregate.register_event("not-an-event")  # type: ignore[arg-type]


def test_domain_exception_str() -> None:
    assert str(DomainException(detail="boom")) == "boom"
    assert str(InvalidDomainEvent()) == "Domain event must inherit Event"


def test_event_defaults() -> None:
    event = MealPlanCreated(user_id=uuid4())
    assert event.event_id is not None
    assert event.created_at is not None


def test_email_and_password_validation() -> None:
    assert Email("user@example.com").to_raw() == "user@example.com"

    with pytest.raises(InvalidEmail):
        Email("invalid-email")

    with pytest.raises(InvalidHashedPassword):
        HashedPassword("")


def test_goal_validation() -> None:
    assert Goal("maintain").to_raw() == "maintain"

    with pytest.raises(InvalidGoal):
        Goal("unknown")


def test_health_params_validation() -> None:
    params = make_health_params()
    params.validate()
    assert params.to_raw()["weight"] == 80.0

    with pytest.raises(InvalidWeight):
        make_health_params(weight=0).validate()

    with pytest.raises(InvalidHeight):
        make_health_params(height=-1).validate()

    with pytest.raises(InvalidAge):
        make_health_params(age=0).validate()

    class FakeLevel:
        value = "invalid"

    with pytest.raises(InvalidActivityLevel):
        HealthParams(
            weight=80,
            height=180,
            age=30,
            gender=GenderType.MALE,
            activity_level=FakeLevel(),  # type: ignore[arg-type]
        ).validate()

    class FakeAllergen:
        value = "invalid"

    with pytest.raises(InvalidAllergen):
        HealthParams(
            weight=80,
            height=180,
            age=30,
            gender=GenderType.MALE,
            activity_level=ActivityLevelType.MEDIUM,
            allergies=[FakeAllergen()],  # type: ignore[list-item]
        ).validate()

    class FakeRestriction:
        value = "invalid"

    with pytest.raises(InvalidRestriction):
        HealthParams(
            weight=80,
            height=180,
            age=30,
            gender=GenderType.MALE,
            activity_level=ActivityLevelType.MEDIUM,
            restrictions=[FakeRestriction()],  # type: ignore[list-item]
        ).validate()

    params_with_lists = make_health_params(
        allergies=[AllergenType.MILK],
        restrictions=[RestrictionType.VEGAN],
    )
    params_with_lists.validate()
    raw = params_with_lists.to_raw()
    assert raw["allergies"] == ["milk"]
    assert raw["restrictions"] == ["vegan"]


def test_session_entity_expiration(monkeypatch: pytest.MonkeyPatch) -> None:
    frozen = datetime(2026, 1, 1, tzinfo=UTC)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):  # noqa: ANN001
            return frozen

    monkeypatch.setattr("src.domain.user.entities.utc_now", lambda: frozen)

    active = SessionEntity(token="t", expires_at=frozen + timedelta(hours=1))
    expired = SessionEntity(token="t", expires_at=frozen - timedelta(hours=1))

    assert active.is_expired() is False
    assert expired.is_expired() is True


def test_user_aggregate_lifecycle() -> None:
    user = make_user()
    user_id = user.id
    email = user.email

    created = UserAggregate.create(email=email, hashed_password=make_hashed_password())
    events = created.pull_events()
    assert isinstance(events[0], UserCreated)

    user.deactivate()
    assert user.is_active is False
    with pytest.raises(UserAlreadyDeactivated):
        user.deactivate()

    user.activate()
    assert user.is_active is True
    with pytest.raises(UserAlreadyActivated):
        user.activate()

    user.promote_to_admin()
    assert user.is_admin is True
    with pytest.raises(UserAlreadyPromoted):
        user.promote_to_admin()

    user.demote_from_admin()
    assert user.is_admin is False
    with pytest.raises(UserAlreadyDemoted):
        user.demote_from_admin()

    new_password = make_hashed_password("new")
    user.change_password(new_password)
    assert user.hashed_password == new_password

    new_email = Email("new@example.com")
    user.change_email(new_email)
    assert user.email == new_email
    with pytest.raises(EmailAlreadySame):
        user.change_email(new_email)

    user.delete()
    assert isinstance(user.pull_events()[-1], UserDeleted)
    assert user.id == user_id


def test_user_sessions() -> None:
    user = make_user()
    expires_at = datetime.now(UTC) + timedelta(days=1)

    user.add_session("token-1", expires_at)
    assert len(user.sessions) == 1
    assert user.sessions is not user._sessions

    user.add_session("token-2", expires_at)
    user.revoke_session("token-2")
    assert len(user.sessions) == 1
    assert user.sessions[0].token == "token-1"

    with pytest.raises(SessionAlreadyExists):
        user.add_session("token-1", expires_at)

    user.revoke_session("token-1")
    assert user.sessions == []

    with pytest.raises(SessionNotFound):
        user.revoke_session("missing")

    user.add_session("token-2", expires_at)
    user.revoke_all_sessions()
    assert user.sessions == []
    assert isinstance(user.pull_events()[-1], UserAllSessionsRevoked)


def test_user_rate_limiting(monkeypatch: pytest.MonkeyPatch) -> None:
    today = date(2026, 8, 3)
    fake_date = type("D", (), {"today": staticmethod(lambda: today)})
    monkeypatch.setattr("src.domain.user.aggregates.date", fake_date)

    user = make_user()
    assert user.can_generate_today() is True

    user.last_request_date = today
    user.daily_requests = DAILY_LIMIT
    assert user.can_generate_today() is False

    user.last_request_date = date(2026, 8, 2)
    assert user.can_generate_today() is True

    user.is_premium = True
    user.last_request_date = today
    user.daily_requests = DAILY_LIMIT
    assert user.can_generate_today() is True

    user.is_premium = False
    user.is_admin = True
    assert user.can_generate_today() is True

    user.is_admin = False
    user.daily_requests = 0
    user.last_request_date = date(2026, 8, 2)
    user.increment_requests()
    assert user.daily_requests == 1
    assert user.last_request_date == today

    user.increment_requests()
    assert user.daily_requests == 2


def test_meal_plan_aggregate_create() -> None:
    user_id = uuid4()
    meal_plan = MealPlanAggregate.create(
        user_id=user_id,
        goal=Goal("gain_muscle"),
        health_params=make_health_params(),
        plan="Plan text",
    )

    events = meal_plan.pull_events()
    assert isinstance(events[0], MealPlanCreated)
    assert meal_plan.user_id == user_id


@pytest.mark.parametrize(
    "exception_cls",
    [
        InvalidGoal,
        InvalidWeight,
        InvalidHeight,
        InvalidAge,
        InvalidActivityLevel,
        InvalidAllergen,
        InvalidRestriction,
        MealPlanNotFound,
        MealPlanGenerationError,
        InvalidEmail,
        InvalidHashedPassword,
        UserAlreadyActivated,
        UserAlreadyDeactivated,
        UserAlreadyPromoted,
        UserAlreadyDemoted,
        SessionAlreadyExists,
        SessionNotFound,
        EmailAlreadySame,
        UserNotFound,
        EmailAlreadyExists,
        PasswordAlreadySame,
        InvalidCredentials,
        UserInactive,
        DailyLimitReached,
    ],
)
def test_exception_defaults(exception_cls: type[DomainException]) -> None:
    exc = exception_cls()
    assert exc.code
    assert exc.detail


def test_user_event_dataclasses() -> None:
    user_id = uuid4()
    email = Email("user@example.com")

    assert UserIsActiveChanged(user_id=user_id, is_active=True).is_active is True
    assert UserIsAdminChanged(user_id=user_id, is_admin=False).is_admin is False
    assert UserPasswordChanged(user_id=user_id).user_id == user_id
    assert UserEmailChanged(user_id=user_id, email=email).email == email
    assert UserSessionCreated(user_id=user_id).user_id == user_id
    assert UserSessionRevoked(user_id=user_id).user_id == user_id
    assert UserAllSessionsRevoked(user_id=user_id).user_id == user_id
