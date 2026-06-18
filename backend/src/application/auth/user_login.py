from datetime import timedelta

from src.application.auth.dto import UserLoginDTO
from src.domain import UserRepository
from src.domain.user.exceptions import InvalidPassword, UserNotFound
from src.domain.user.value_objects import Email
from src.infrastructure.auth.hasher import PasswordHasher
from src.infrastructure.auth.session import generate_session_token
from src.shared.time_utils import utc_now


class UserLoginUseCase:
    """User login Use Case."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, email: str, password: str) -> UserLoginDTO:
        """Execute log in."""
        # Check if user exists
        user = await self.user_repository.get_by_email(Email(email))
        if not user:
            raise UserNotFound()

        # Verify password
        if not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidPassword()

        # Create session and add to user
        session_token = generate_session_token()
        user.add_session(
            token=session_token,
            expires_at=utc_now() + timedelta(days=7),
        )

        # Save user to database
        await self.user_repository.update(user)

        return UserLoginDTO(id=user.id, email=user.email, session_token=session_token)
