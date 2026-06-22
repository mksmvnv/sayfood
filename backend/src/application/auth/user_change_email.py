from src.application.auth.dto import UserChangeEmailDTO
from src.domain.user.exceptions import (
    EmailAlreadyExists,
    EmailAlreadySame,
    InvalidCredentials,
    SessionNotFound,
    UserNotFound,
)
from src.domain.user.repositories import UserRepository
from src.domain.user.value_objects import Email


class UserChangeEmailUseCase:
    """User change email Use Case."""

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def execute(
        self,
        session_token: str | None,
        old_email: str,
        new_email: str,
    ) -> UserChangeEmailDTO:
        """Execute email changing."""
        # Check if session exists
        if session_token is None:
            raise SessionNotFound()

        # Get current user by session token
        user = await self.user_repository.get_by_session_token(session_token)
        if not user:
            raise UserNotFound()

        # Check old email matches current email
        if user.email.to_raw() != old_email:
            raise InvalidCredentials()

        # Check new email is not the same as old
        if old_email == new_email:
            raise EmailAlreadySame()

        # Check new email is not already taken
        existing_user = await self.user_repository.get_by_email(Email(new_email))
        if existing_user:
            raise EmailAlreadyExists()

        # Update email
        user.change_email(Email(new_email))

        # Revoke all sessions
        user.revoke_all_sessions()

        # Update user in database
        await self.user_repository.update(user)

        return UserChangeEmailDTO()
