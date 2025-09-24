import secrets
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.request import Request

from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.apps.users.tasks import send_recovery_email_task
from server.apps.users.validators import validate_request
from server.common.constants import DATA_LENGHT
from server.di import resolve


def pass_recovery_processing(request: Request) -> Any | None:
    """Processes the POST request for password recovery."""
    email = validate_request(request)
    try:
        user = resolve(UserRepo).get_by_email(email)
    except ObjectDoesNotExist:
        return None
    new_password = secrets.token_urlsafe(DATA_LENGHT)
    resolve(UserRepoSave).update_password(user, new_password)
    return send_recovery_email_task.delay(
        to_email=user.email, new_password=new_password
    )
