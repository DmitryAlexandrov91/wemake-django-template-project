import secrets

import pytest

from server.apps.users.models import (
    REGISTRATION_EMAIL_REQUIRED_ERROR,
    CustomUser,
)


@pytest.mark.django_db
def test_create_user_without_email_raises_error() -> None:
    """Ensure that creating a user without email raises ValueError."""
    with pytest.raises(ValueError, match=REGISTRATION_EMAIL_REQUIRED_ERROR):
        CustomUser.objects.create_user(
            email='',
            password=secrets.token_urlsafe(12),
        )


@pytest.mark.django_db
def test_create_user_successfully() -> None:
    """Ensure that user is created successfully with valid data."""
    email = 'test@example.com'
    full_name = 'test_name'
    password = secrets.token_urlsafe(12)
    user = CustomUser.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
    )
    assert user is not None
    assert user.email == email
    assert user.full_name == full_name
    assert user.check_password(password)
