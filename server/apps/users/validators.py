import re
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.request import Request


def validate_request(request: Request) -> str | None:
    """Check and return a valid email in request data."""
    email = request.data.get('email')
    if not email:
        return None
    try:
        validate_email(email)
    except Exception:
        return None
    return str(email)


def validate_telegram_username(username: Any) -> None:
    """Check Telegram username."""
    if not isinstance(username, str):
        raise ValidationError('Telegram username must be a string.')
    pattern = r'^@[A-Za-z0-9][A-Za-z0-9_]+$'
    if not re.fullmatch(pattern, username):
        raise ValidationError(
            'Telegram username should begin with @ '
            'and contain only latin lletters, digits and underscore.'
        )
