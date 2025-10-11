from django.core.exceptions import ValidationError

from server.apps.users.models import CustomUser


def validate_unique_email(email: str) -> None:
    """Validate unique email."""
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError(f'Email {email} already exists')
