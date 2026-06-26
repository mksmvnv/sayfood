from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from src.domain.meal_plan.exceptions import (
    InvalidActivityLevel,
    InvalidAge,
    InvalidGoal,
    InvalidHeight,
    InvalidWeight,
)
from src.domain.seedwork.value_objects import ValueObject


class GoalType(StrEnum):
    """Goal type enum."""

    LOSE_WEIGHT = "lose_weight"
    GAIN_MUSCLE = "gain_muscle"
    MAINTAIN = "maintain"


class ActivityLevelType(StrEnum):
    """Activity level type enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


VALID_GOALS = {g.value for g in GoalType}
VALID_ACTIVITY_LEVELS = {al.value for al in ActivityLevelType}


@dataclass(frozen=True)
class Goal(ValueObject[str]):
    """Goal value object."""

    value: str

    def validate(self) -> None:
        """Validate goal."""
        if self.value not in VALID_GOALS:
            raise InvalidGoal()

    def to_raw(self) -> str:
        """Return raw value."""
        return self.value


@dataclass(frozen=True)
class HealthParams:
    """Health parameters value object."""

    weight: float
    height: float
    age: int
    activity_level: ActivityLevelType
    allergies: list[str] | None = None
    restrictions: list[str] | None = None

    def validate(self) -> None:
        """Validate health params."""
        if self.weight <= 0:
            raise InvalidWeight()
        if self.height <= 0:
            raise InvalidHeight()
        if self.age < 1 or self.age > 120:
            raise InvalidAge()
        if self.activity_level.value not in VALID_ACTIVITY_LEVELS:
            raise InvalidActivityLevel()

    def to_raw(self) -> dict[str, Any]:
        """Return raw value."""
        return {
            "weight": self.weight,
            "height": self.height,
            "age": self.age,
            "activity_level": self.activity_level.value,
            "allergies": self.allergies or [],
            "restrictions": self.restrictions or [],
        }
