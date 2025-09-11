from typing import Any

import pytest
from django.core.exceptions import ValidationError

from server.apps.users.validators import validate_request


@pytest.mark.django_db
def test_valid_request(valid_request: Any) -> None:
    """Tests validation of a valid request."""
    assert validate_request(valid_request) == valid_request.data['email']


@pytest.mark.django_db
def test_wrong_request(wrong_request: Any) -> None:
    """Tests a request with invalid email."""
    with pytest.raises(ValidationError):
        validate_request(wrong_request)


@pytest.mark.django_db
def test_empty_request(empty_request: Any) -> None:
    """Tests an empty email request."""
    with pytest.raises(ValidationError):
        validate_request(empty_request)
