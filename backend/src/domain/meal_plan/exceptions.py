from dataclasses import dataclass

from src.domain.seedwork.exceptions import DomainException


@dataclass(eq=False)
class InvalidGoal(DomainException):
    """Raised when goal is invalid."""

    code: str = "invalid_goal"
    detail: str = "Invalid goal"


@dataclass(eq=False)
class InvalidWeight(DomainException):
    """Raised when weight is invalid."""

    code: str = "invalid_weight"
    detail: str = "Invalid weight"


@dataclass(eq=False)
class InvalidHeight(DomainException):
    """Raised when height is invalid."""

    code: str = "invalid_height"
    detail: str = "Invalid height"


@dataclass(eq=False)
class InvalidAge(DomainException):
    """Raised when age is invalid."""

    code: str = "invalid_age"
    detail: str = "Invalid age"


@dataclass(eq=False)
class InvalidActivityLevel(DomainException):
    """Raised when activity level is invalid."""

    code: str = "invalid_activity_level"
    detail: str = "Invalid activity level"


@dataclass(eq=False)
class MealPlanNotFound(DomainException):
    """Raised when meal plan not found."""

    code: str = "meal_plan_not_found"
    detail: str = "Meal plan not found"
