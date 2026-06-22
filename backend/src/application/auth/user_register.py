from src.application.auth.dto import UserRegisterDTO
from src.domain.user.aggregates import UserAggregate
from src.domain.user.exceptions import EmailAlreadyExists
from src.domain.user.repositories import UserRepository
from src.domain.user.value_objects import Email
from src.infrastructure.auth.hasher import PasswordHasher


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
        user = await self.user_repository.get_by_email(Email(email))
        if user:
            raise EmailAlreadyExists()

        # Hash password
        hashed_password = self.password_hasher.hash(password)

        # Create domain user
        new_user = UserAggregate.create(
            email=Email(email),
            hashed_password=hashed_password,
        )

        # Save user to database
        await self.user_repository.add(new_user)

        return UserRegisterDTO(id=new_user.id, email=new_user.email)
