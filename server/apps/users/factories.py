from typing import TYPE_CHECKING, Any

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

if TYPE_CHECKING:
    from server.apps.users.models import CustomUser

User = get_user_model()


class UserFactory(DjangoModelFactory):  # type: ignore[type-arg, misc, unused-ignore]
    """Factory for creating CustomUser instances."""

    class Meta:
        model: type['CustomUser'] = User
        skip_postgeneration_save = True

    email: Any = factory.LazyAttributeSequence(  # type: ignore[attr-defined, no-untyped-call, unused-ignore]
        lambda _obj, idx: f'testuser{idx}@example.com'  # noqa: WPS110
    )
    full_name: str = 'Test User'

    password: Any = factory.PostGenerationMethodCall(  # type: ignore[attr-defined, no-untyped-call, unused-ignore]
        'set_password', 'testpass'
    )
