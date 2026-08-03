
import pytest

from src.application.auth.user_change_email import UserChangeEmailUseCase
from src.application.auth.user_change_password import UserChangePasswordUseCase
from src.application.auth.user_login import UserLoginUseCase
from src.application.auth.user_logout import UserLogoutUseCase
from src.application.auth.user_register import UserRegisterUseCase
from src.domain.user.exceptions import (
    EmailAlreadyExists,
    EmailAlreadySame,
    InvalidCredentials,
    PasswordAlreadySame,
    SessionNotFound,
    UserInactive,
    UserNotFound,
)
from src.domain.user.value_objects import Email
from tests.conftest import FakeUserRepository, add_session, make_user, password_hasher


@pytest.mark.asyncio
async def test_user_register_success(password_hasher: password_hasher) -> None:
    repo = FakeUserRepository()
    use_case = UserRegisterUseCase(repo, password_hasher)

    result = await use_case.execute("new@example.com", "password123")

    assert result.email.to_raw() == "new@example.com"
    assert len(repo.users) == 1


@pytest.mark.asyncio
async def test_user_register_duplicate_email(password_hasher: password_hasher) -> None:
    repo = FakeUserRepository()
    user = make_user("exists@example.com")
    await repo.add(user)
    use_case = UserRegisterUseCase(repo, password_hasher)

    with pytest.raises(EmailAlreadyExists):
        await use_case.execute("exists@example.com", "password123")


@pytest.mark.asyncio
async def test_user_login_success(password_hasher: password_hasher) -> None:
    repo = FakeUserRepository()
    plain = "password123"
    user = make_user(hashed_password=password_hasher.hash(plain).to_raw())
    await repo.add(user)
    use_case = UserLoginUseCase(repo, password_hasher)

    result = await use_case.execute("user@example.com", plain)

    assert result.session_token
    updated = await repo.get_by_email(Email("user@example.com"))
    assert updated is not None
    assert updated.sessions


@pytest.mark.asyncio
async def test_user_login_failures(password_hasher: password_hasher) -> None:
    repo = FakeUserRepository()
    use_case = UserLoginUseCase(repo, password_hasher)

    with pytest.raises(UserNotFound):
        await use_case.execute("missing@example.com", "password123")

    inactive = make_user(is_active=False)
    await repo.add(inactive)
    with pytest.raises(UserInactive):
        await use_case.execute("user@example.com", "password123")

    active = make_user("active@example.com", password_hasher.hash("correct").to_raw())
    await repo.add(active)
    with pytest.raises(InvalidCredentials):
        await use_case.execute("active@example.com", "wrongpass1")


@pytest.mark.asyncio
async def test_user_logout_success() -> None:
    repo = FakeUserRepository()
    user = make_user()
    add_session(user, "logout-token")
    await repo.add(user)
    use_case = UserLogoutUseCase(repo)

    await use_case.execute("logout-token")

    updated = await repo.get_by_session_token("logout-token")
    assert updated is None


@pytest.mark.asyncio
async def test_user_logout_failures() -> None:
    repo = FakeUserRepository()
    use_case = UserLogoutUseCase(repo)

    with pytest.raises(SessionNotFound):
        await use_case.execute(None)

    with pytest.raises(UserNotFound):
        await use_case.execute("missing-token")


@pytest.mark.asyncio
async def test_user_change_password_success(password_hasher: password_hasher) -> None:
    repo = FakeUserRepository()
    old = "password123"
    user = make_user(hashed_password=password_hasher.hash(old).to_raw())
    add_session(user, "pwd-token")
    await repo.add(user)
    use_case = UserChangePasswordUseCase(repo, password_hasher)

    await use_case.execute("pwd-token", old, "newpassword1")

    updated = await repo.get_by_id(user.id)
    assert updated is not None
    assert updated.sessions == []
    assert password_hasher.verify("newpassword1", updated.hashed_password)


@pytest.mark.asyncio
async def test_user_change_password_failures(password_hasher: password_hasher) -> None:
    repo = FakeUserRepository()
    use_case = UserChangePasswordUseCase(repo, password_hasher)

    with pytest.raises(SessionNotFound):
        await use_case.execute(None, "password123", "newpassword1")

    with pytest.raises(UserNotFound):
        await use_case.execute("missing", "password123", "newpassword1")

    user = make_user(hashed_password=password_hasher.hash("password123").to_raw())
    add_session(user, "token")
    await repo.add(user)

    with pytest.raises(InvalidCredentials):
        await use_case.execute("token", "wrongpass1", "newpassword1")

    with pytest.raises(PasswordAlreadySame):
        await use_case.execute("token", "password123", "password123")


@pytest.mark.asyncio
async def test_user_change_email_success() -> None:
    repo = FakeUserRepository()
    user = make_user("old@example.com")
    add_session(user, "email-token")
    await repo.add(user)
    use_case = UserChangeEmailUseCase(repo)

    await use_case.execute("email-token", "old@example.com", "new@example.com")

    updated = await repo.get_by_id(user.id)
    assert updated is not None
    assert updated.email.to_raw() == "new@example.com"
    assert updated.sessions == []


@pytest.mark.asyncio
async def test_user_change_email_failures() -> None:
    repo = FakeUserRepository()
    use_case = UserChangeEmailUseCase(repo)

    with pytest.raises(SessionNotFound):
        await use_case.execute(None, "old@example.com", "new@example.com")

    with pytest.raises(UserNotFound):
        await use_case.execute("missing", "old@example.com", "new@example.com")

    user = make_user("old@example.com")
    add_session(user, "token")
    await repo.add(user)

    with pytest.raises(InvalidCredentials):
        await use_case.execute("token", "wrong@example.com", "new@example.com")

    with pytest.raises(EmailAlreadySame):
        await use_case.execute("token", "old@example.com", "old@example.com")

    other = make_user("taken@example.com")
    await repo.add(other)
    with pytest.raises(EmailAlreadyExists):
        await use_case.execute("token", "old@example.com", "taken@example.com")
