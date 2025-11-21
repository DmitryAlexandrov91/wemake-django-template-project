import secrets

import pytest
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.users.admin import CustomUserAdmin
from server.apps.users.models import CustomUser
from tests.plugins.fakery import FakeryM

LOGIN_URL = reverse('login')
REFRESH_URL = reverse('token_refresh')
LOGOUT_URL = reverse('logout')

JWT_COOKIE_ACCESS_NAME = 'ACCESS_NAME'
JWT_COOKIE_REFRESH_NAME = 'REFRESH_NAME'


@pytest.fixture
def api_client() -> APIClient:
    """API client."""
    return APIClient()


@pytest.fixture
def password() -> str:
    """Fixture returns password for creating user."""
    return secrets.token_urlsafe()


@pytest.fixture
def user(fakery_m: FakeryM[CustomUser], password: str) -> CustomUser:
    """Create user."""
    user_factory = fakery_m(CustomUser)
    return user_factory(password=password)


@pytest.fixture
def auth_client(api_client: APIClient, auth_user: CustomUser) -> APIClient:
    """Return an authenticated APIClient for testing."""
    api_client.force_authenticate(user=auth_user)
    return api_client


@pytest.fixture
def auth_client_user_without_department(
    api_client: APIClient,
    user: CustomUser,
) -> APIClient:
    """Return an authenticated APIClient for testing."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user_admin_instance() -> CustomUserAdmin:
    """UserAdmin fixture."""
    return CustomUserAdmin(CustomUser, AdminSite())
