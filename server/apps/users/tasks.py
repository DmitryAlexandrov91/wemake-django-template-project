from collections.abc import Callable

from celery import shared_task
from django.core.mail import send_mail

from server.settings.components import common

TaskFunction = Callable[[str, str], bool]


@shared_task  # type: ignore[misc]
def send_recovery_email_task(to_email: str, new_string: str) -> int:
    """Celery task for sending recovery email."""
    return send_mail(
        subject='Password reset',
        message=f'The new password for the account is {new_string}.',
        from_email=common.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )
