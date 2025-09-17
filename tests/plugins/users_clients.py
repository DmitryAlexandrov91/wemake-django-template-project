import pytest
from rest_framework.test import APIClient

from server.apps.users.models import CustomUser


@pytest.fixture
def api_client() -> APIClient:
    """API client."""
    return APIClient()


@pytest.fixture
def api_client_auth(
    api_client: APIClient,
    auth_user: CustomUser,
) -> APIClient:
    """API client authenticated."""
    api_client.force_authenticate(user=auth_user)
    return api_client
