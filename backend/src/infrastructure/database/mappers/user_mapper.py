from src.domain.user.aggregates import User as UserAggregate
from src.domain.user.value_objects import Email, HashedPassword
from src.infrastructure.database.models import User as UserModel


def user_to_model(user: UserAggregate) -> UserModel:
    """Convert domain User to ORM UserModel."""
    return UserModel(
        id=user.id,
        email=user.email.to_raw(),
        hashed_password=user.hashed_password.to_raw(),
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def user_to_domain(model: UserModel) -> UserAggregate:
    """Convert ORM UserModel to domain User."""
    return UserAggregate(
        id=model.id,
        email=Email(model.email),
        hashed_password=HashedPassword(model.hashed_password),
        is_active=model.is_active,
        is_admin=model.is_admin,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
