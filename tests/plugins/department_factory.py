from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypedDict, Unpack

import pytest

from server.apps.company.models import Department

if TYPE_CHECKING:
    from tests.plugins.fakery import FakeryM


type DepartmentFactory = Callable[
    [Unpack[_DepartmentFactoryParams]], Department
]

type DepartmentBatchFactory = Callable[[int], list[Department]]


class _DepartmentFactoryParams(TypedDict, total=False):
    """Base params for DepartmentFactory."""

    name: str
    description: str
    head: Any


@pytest.fixture
def department_factory(fakery_m: FakeryM[Department]) -> DepartmentFactory:
    """Return a factory to create Department instances with custom fields."""

    def factory(**kwargs: Unpack[_DepartmentFactoryParams]) -> Department:
        return fakery_m(Department)(**kwargs)

    return factory


@pytest.fixture
def department_batch(
    department_factory: DepartmentFactory,
) -> DepartmentBatchFactory:
    """Return a factory that creates `batch_size` Department instances."""

    def factory(batch_size: int) -> list[Department]:
        return [
            department_factory(name=f'Dep{dep_number}')
            for dep_number in range(batch_size)
        ]

    return factory


@pytest.fixture
def department(department_factory: DepartmentFactory) -> Department:
    """Return a single Department instance created."""
    return department_factory(name='Unique Department')
