import secrets


def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)
