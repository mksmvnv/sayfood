import bcrypt

from src.domain.user.value_objects import HashedPassword


class PasswordHasher:
    """Password hasher."""

    def hash(self, plain_password: str) -> HashedPassword:
        """Hash a plain password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode(), salt)
        return HashedPassword(hashed.decode())

    def verify(self, plain_password: str, hashed_password: HashedPassword) -> bool:
        """Verify a plain password against a hashed password."""
        return bcrypt.checkpw(
            plain_password.encode(),
            hashed_password.to_raw().encode(),
        )
