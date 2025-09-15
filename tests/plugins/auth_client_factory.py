from collections.abc import Callable

import pytest
from rest_framework.test import APIClient

from server.apps.users.models import CustomUser

type AuthClientFactory = Callable[[CustomUser], APIClient]


@pytest.fixture
def auth_client_factory() -> AuthClientFactory:
    """Factory returning APIClient authenticated with given user."""

    def factory(user: CustomUser) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    return factory
