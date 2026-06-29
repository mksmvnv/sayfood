from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from src.domain.meal_plan.exceptions import (
    InvalidActivityLevel,
    InvalidAge,
    InvalidAllergen,
    InvalidGoal,
    InvalidHeight,
    InvalidRestriction,
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


class AllergenType(StrEnum):
    """Common allergens enum."""

    MILK = "milk"
    EGGS = "eggs"
    PEANUTS = "peanuts"
    TREE_NUTS = "tree_nuts"
    SESAME = "sesame"
    FISH = "fish"
    SHELLFISH = "shellfish"
    WHEAT = "wheat"
    SOY = "soy"


class RestrictionType(StrEnum):
    """Common dietary restrictions enum."""

    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    LACTOSE_FREE = "lactose_free"
    KETO = "keto"
    HALAL = "halal"
    KOSHER = "kosher"


VALID_GOALS = {g.value for g in GoalType}
VALID_ACTIVITY_LEVELS = {al.value for al in ActivityLevelType}
VALID_ALLERGENS = {a.value for a in AllergenType}
VALID_RESTRICTIONS = {r.value for r in RestrictionType}


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
    allergies: list[AllergenType] | None = None
    restrictions: list[RestrictionType] | None = None

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
        if self.allergies:
            for allergen in self.allergies:
                if allergen.value not in VALID_ALLERGENS:
                    raise InvalidAllergen()
        if self.restrictions:
            for restriction in self.restrictions:
                if restriction.value not in VALID_RESTRICTIONS:
                    raise InvalidRestriction()

    def to_raw(self) -> dict[str, Any]:
        """Return raw value."""
        return {
            "weight": self.weight,
            "height": self.height,
            "age": self.age,
            "activity_level": self.activity_level.value,
            "allergies": [a.value for a in self.allergies] if self.allergies else [],
            "restrictions": [r.value for r in self.restrictions] if self.restrictions else [],
        }
