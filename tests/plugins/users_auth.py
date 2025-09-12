import secrets

import pytest
from django.urls import reverse

from server.apps.users.models import CustomUser
from tests.plugins.fakery import FakeryM

LOGIN_URL = reverse('login')
REFRESH_URL = reverse('token_refresh')
LOGOUT_URL = reverse('logout')

JWT_COOKIE_ACCESS_NAME = 'ACCESS_NAME'
JWT_COOKIE_REFRESH_NAME = 'REFRESH_NAME'


@pytest.fixture
def password() -> str:
    """Fixture returns password for creating user."""
    return secrets.token_urlsafe()


@pytest.fixture
def user(fakery_m: FakeryM[CustomUser], password: str) -> CustomUser:
    """Create user."""
    user_factory = fakery_m(CustomUser)
    return user_factory(password=password)
