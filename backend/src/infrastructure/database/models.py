from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import BaseModel


class UserModel(BaseModel):
    """User model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    daily_requests: Mapped[int] = mapped_column(Integer, default=0)
    last_request_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)


class SessionModel(BaseModel):
    """Session model."""

    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class MealPlanModel(BaseModel):
    """Meal plan model."""

    __tablename__ = "meal_plans"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    goal: Mapped[str] = mapped_column(String)
    weight: Mapped[float] = mapped_column(Float)
    height: Mapped[float] = mapped_column(Float)
    age: Mapped[int] = mapped_column(Integer)
    activity_level: Mapped[str] = mapped_column(String)
    allergies: Mapped[str | None] = mapped_column(String, nullable=True)
    restrictions: Mapped[str | None] = mapped_column(String, nullable=True)
    plan: Mapped[str] = mapped_column(Text)
