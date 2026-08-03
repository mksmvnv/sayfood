import inspect

import pytest

from src.domain.meal_plan.repositories import MealPlanRepository
from src.domain.seedwork.value_objects import ValueObject
from src.domain.user.repositories import UserRepository


class _ConcreteValueObject(ValueObject[str]):
    value: str

    def validate(self) -> None:
        return None

    def to_raw(self) -> str:
        return self.value


def test_value_object_abstract_methods() -> None:
    base_validate = ValueObject.validate
    base_to_raw = ValueObject.to_raw

    with pytest.raises(NotImplementedError):
        base_validate(_ConcreteValueObject(value="x"))

    with pytest.raises(NotImplementedError):
        base_to_raw(_ConcreteValueObject(value="x"))


@pytest.mark.asyncio
@pytest.mark.parametrize("repository_cls", [UserRepository, MealPlanRepository])
async def test_repository_abstract_methods(repository_cls: type) -> None:
    for name, method in inspect.getmembers(repository_cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        with pytest.raises(NotImplementedError):
            result = method(repository_cls, object())  # type: ignore[arg-type]
            if inspect.iscoroutine(result):
                await result
