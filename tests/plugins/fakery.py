from collections.abc import Callable
from typing import Protocol

import pytest
from django.db import models
from django_fakery.faker_factory import Factory


class FakeryM[Model: models.Model](Protocol):
    """Protocol to create fake django models."""

    def __call__(
        self,
        model_type: type[Model],
    ) -> Callable[..., Model]:
        """Further callable accepts kwargs that any model has."""


@pytest.fixture
def fakery_m[Model: models.Model](
    fakery: Factory[Model],
    monkeypatch: pytest.MonkeyPatch,
) -> FakeryM[Model]:
    """Provide a type safe interface for `django-fakery`."""
    # TODO: remove after https://github.com/fcurella/django-fakery/pull/77
    # will be merged.
    monkeypatch.setitem(fakery.field_names, 'full_name', ('name', (), {}))

    def factory(model_type: type[Model]) -> Callable[..., Model]:
        return fakery.m(  # type: ignore[call-overload, no-any-return]
            model_type,
        )

    return factory
