import secrets
from typing import Any

from django.core.exceptions import ObjectDoesNotExist

from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.apps.users.tasks import send_recovery_email_task
from server.common.constants import DATA_LENGTH
from server.di import resolve


def pass_recovery_processing(email: str) -> Any | None:
    """Processes the POST request for password recovery."""
    try:
        user = resolve(UserRepo).get_by_email(email)
    except ObjectDoesNotExist:
        return None
    new_password = secrets.token_urlsafe(DATA_LENGTH)
    resolve(UserRepoSave).update_password(user, new_password)
    return send_recovery_email_task.delay(
        to_email=user.email, new_password=new_password
    )
