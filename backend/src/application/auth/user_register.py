from datetime import timedelta

from src.application.auth.dto import UserDTO, UserRegisterDTO
from src.domain import UserRepository
from src.domain.user.aggregates import UserAggregate
from src.domain.user.exceptions import EmailAlreadyExists
from src.domain.user.value_objects import Email
from src.infrastructure.auth.hasher import PasswordHasher
from src.infrastructure.auth.session import generate_session_token
from src.shared.time_utils import utc_now


class UserRegisterUseCase:
    """User register Use Case."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, email: str, password: str) -> UserRegisterDTO:
        """Execute registration."""
        # Check if user exists
        existing_user = await self.user_repository.get_by_email(Email(email))
        if existing_user:
            raise EmailAlreadyExists()

        # Hash password
        hashed_password = self.password_hasher.hash(password)

        # Create domain user
        user = UserAggregate.create(
            email=Email(email),
            hashed_password=hashed_password,
        )

        # Create session and add to user
        session_token = generate_session_token()
        user.add_session(
            token=session_token,
            expires_at=utc_now() + timedelta(days=7),
        )

        # Save user to database
        await self.user_repository.add(user)

        return UserRegisterDTO(
            user=UserDTO(
                id=user.id,
                email=user.email.to_raw(),
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
            ),
            session_token=session_token,
        )
