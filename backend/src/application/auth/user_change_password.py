from src.application.auth.dto import UserChangePasswordDTO
from src.domain.user.exceptions import (
    InvalidCredentials,
    PasswordAlreadySame,
    SessionNotFound,
    UserNotFound,
)
from src.domain.user.repositories import UserRepository
from src.infrastructure.auth.hasher import PasswordHasher


class UserChangePasswordUseCase:
    """User change password Use Case."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(
        self, session_token: str | None, old_password: str, new_password: str
    ) -> UserChangePasswordDTO:
        """Execute password changing."""
        # Check if session exists
        if session_token is None:
            raise SessionNotFound()

        # Check if user exists
        user = await self.user_repository.get_by_session_token(session_token)
        if not user:
            raise UserNotFound()

        # Verify password
        if not self.password_hasher.verify(old_password, user.hashed_password):
            raise InvalidCredentials()

        # Check new password is not the same as old
        if self.password_hasher.verify(new_password, user.hashed_password):
            raise PasswordAlreadySame()

        # Hash new password and update
        new_hashed_password = self.password_hasher.hash(new_password)
        user.change_password(new_hashed_password)

        # Revoke all sessions
        user.revoke_all_sessions()

        # Update user in database
        await self.user_repository.update(user)

        return UserChangePasswordDTO()
