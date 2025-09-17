from dataclasses import dataclass

import pytest

from server.apps.company.models import Department

email = 'email'


@dataclass
class RequestMock:
    """Mocking request."""

    data: dict[str, str | int]  # noqa: WPS110


@pytest.fixture
def valid_request() -> RequestMock:
    """Fixture for a valid request."""
    return RequestMock(data={email: 'test@email.com'})


@pytest.fixture
def wrong_request() -> RequestMock:
    """Fixture for an invalid email request."""
    return RequestMock(data={email: 'invalid-email'})


@pytest.fixture
def empty_request() -> RequestMock:
    """Fixture for empty email request."""
    return RequestMock(data={})


@pytest.fixture
def employee_create_request(
    valid_request: RequestMock, department: Department
) -> RequestMock:
    """Fixture for creating request with sample data."""
    return RequestMock(
        data={
            'full_name': 'Test Employee',
            'email': valid_request.data[email],
            'department': department.pk,
            'tg_id': '123456789',
        }
    )


@pytest.fixture
def employee_create_wrong_request(wrong_request: RequestMock) -> RequestMock:
    """Fixture for creating request with sample data."""
    return RequestMock(
        data={
            'full_name': 'Test Employee',
            'email': wrong_request.data[email],
            'tg_id': '123456789',
        }
    )
