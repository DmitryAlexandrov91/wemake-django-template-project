import secrets
from smtplib import SMTPException
from typing import Any

import pytest
from pytest_mock import MockFixture

from server.apps.users.tasks import send_recovery_email_task
from server.common.constants import DATA_LENGHT

to_email = 'test@example.com'
new_password = secrets.token_urlsafe(DATA_LENGHT)


@pytest.fixture
def mocked_send_mail(mocker: MockFixture) -> Any:
    """Mock the email sending task fixture."""
    return mocker.patch('server.apps.users.tasks.send_mail', return_value=True)


@pytest.fixture
def mocked_send_mail_error(mocker: MockFixture) -> Any:
    """Mock the email sending task fixture."""
    return mocker.patch(
        'server.apps.users.tasks.send_mail',
        side_effect=SMTPException('Mocked SMTP error'),
    )


@pytest.mark.django_db
def test_send_recovery_email_success(mocked_send_mail: Any) -> None:
    """Testing successful email sending."""
    assert send_recovery_email_task(to_email, new_password) == 1


@pytest.mark.django_db
def test_send_recovery_email_failure(mocked_send_mail_error: Any) -> None:
    """Testing email sending failure."""
    with pytest.raises(SMTPException):
        send_recovery_email_task(to_email, new_password)
    mocked_send_mail_error.assert_called_once()
