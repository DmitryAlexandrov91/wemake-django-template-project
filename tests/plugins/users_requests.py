from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class RequestMock:
    """Mocking request."""

    data: dict[str, str]  # noqa: WPS110


@pytest.fixture
def valid_request() -> Any:
    """Fixture for a valid request."""
    return RequestMock(data={'email': 'test@email.com'})


@pytest.fixture
def wrong_request() -> Any:
    """Fixture for an invalid email request."""
    return RequestMock(data={'email': 'invalid-email'})


@pytest.fixture
def empty_request() -> Any:
    """Fixture for empty email request."""
    return RequestMock(data={})
