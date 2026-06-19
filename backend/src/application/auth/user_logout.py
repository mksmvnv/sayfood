from src.application.auth.dto import UserLogoutDTO
from src.domain import UserRepository
from src.domain.user.exceptions import SessionNotFound, UserNotFound


class UserLogoutUseCase:
    """User logout Use Case."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, session_token: str | None) -> UserLogoutDTO:
        """Execute log out."""
        # Check if session exists
        if session_token is None:
            raise SessionNotFound()

        # Check if user exists
        user = await self.user_repository.get_by_session_token(session_token)
        if not user:
            raise UserNotFound()

        # Revoke session
        user.revoke_session(session_token)

        # Update user in database
        await self.user_repository.update(user)

        return UserLogoutDTO()
