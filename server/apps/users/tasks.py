from collections.abc import Callable

from celery import group, shared_task
from django.core.mail import send_mail

from server.apps.users.infra.repository import UserRepoSave
from server.di import resolve
from server.settings.components import common

TaskFunction = Callable[[str, str], bool]


@shared_task  # type: ignore[misc]
def send_recovery_email_task(to_email: str, new_password: str) -> int:
    """Celery task for sending recovery email."""
    return send_mail(
        subject='Password reset',
        message=f'The new password for the account is {new_password}.',
        from_email=common.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )


@shared_task  # type: ignore[misc]
def inactivate_single_user_task(user_id: int) -> None:
    """Celery task for inactivating one user."""
    resolve(UserRepoSave).mark_inactive(pk=user_id)


@shared_task  # type: ignore[misc]
def inactivate_marked_users_task() -> None:
    """Celery task to inactivate users."""
    user_ids = resolve(UserRepoSave).get_all_to_inactivate_ids()
    update_group = group(
        inactivate_single_user_task.s(user_id=user_id) for user_id in user_ids
    )
    update_group.apply_async()
