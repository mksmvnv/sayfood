from src.domain.user.aggregates import UserAggregate
from src.domain.user.value_objects import Email, HashedPassword
from src.infrastructure.database.models import SessionModel, UserModel


def user_to_model(user_aggregate: UserAggregate) -> UserModel:
    """Convert domain User to ORM UserModel."""
    return UserModel(
        id=user_aggregate.id,
        email=user_aggregate.email.to_raw(),
        hashed_password=user_aggregate.hashed_password.to_raw(),
        is_active=user_aggregate.is_active,
        is_admin=user_aggregate.is_admin,
        daily_requests=user_aggregate.daily_requests,
        last_request_date=user_aggregate.last_request_date,
        is_premium=user_aggregate.is_premium,
        created_at=user_aggregate.created_at,
        updated_at=user_aggregate.updated_at,
    )


def user_to_domain(
    user_model: UserModel,
    session_models: list[SessionModel] | None = None,
) -> UserAggregate:
    """Convert ORM UserModel to domain User."""
    user = UserAggregate(
        id=user_model.id,
        email=Email(user_model.email),
        hashed_password=HashedPassword(user_model.hashed_password),
        is_active=user_model.is_active,
        is_admin=user_model.is_admin,
        daily_requests=user_model.daily_requests,
        last_request_date=user_model.last_request_date,
        is_premium=user_model.is_premium,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )

    # Add sessions to user aggregate
    if session_models:
        for session_model in session_models:
            user.add_session(
                token=session_model.token,
                expires_at=session_model.expires_at,
            )

    return user
