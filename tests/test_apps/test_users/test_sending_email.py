import secrets
from smtplib import SMTPException
from typing import Any
from unittest.mock import Mock, patch

import pytest
from pytest_mock import MockFixture

from server.apps.surveys.tasks import email_survey_invitation_task
from server.apps.users.tasks import send_recovery_email_task
from server.common.constants import DATA_LENGTH

to_email = 'test@example.com'
new_password = secrets.token_urlsafe(DATA_LENGTH)


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


@patch('server.apps.surveys.tasks.tasks.send_mail')
def test_email_survey_invitation_task_sends_mail(mock_emailing: Mock) -> None:
    """Test sending email."""
    from_email = 'noreply@example.com'
    to_emails = ['user1@example.com', 'user2@example.com']

    email_survey_invitation_task(
        subject='Subject',
        message='Message',
        from_email=from_email,
        to_emails=to_emails,
    )
    mock_emailing.assert_called_once()
