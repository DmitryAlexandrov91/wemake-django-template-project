from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
)
from server.apps.surveys.models import Question, Survey
from server.apps.tgbot import usecases
from server.apps.tgbot.handlers.start import StartHandlerService
from server.apps.tgbot.usecases.validators import recognize_survey_id
from server.apps.users.infra.repository import UserRepo
from server.apps.users.models import CustomUser
from server.common.layouts import SURVEY_KEY

START_PREFIX = '/start '


@patch('server.apps.users.infra.repository.UserRepo')
@patch('server.apps.surveys.infra.repository.SurveyRepo')
@patch('server.apps.surveys.infra.repository.SurveyResultRepo')
def test_start_handler_service_new(
    mock_survey_res_repo: Mock,
    mock_survey_repo: Mock,
    mock_user_repo: Mock,
    mock_bot: Mock,
    message_with_user: Mock,
) -> None:
    """Test StartHandlerService."""
    mock_user = Mock()
    mock_survey = Mock()
    mock_user_repo.get_by_tg_username.return_value = mock_user
    mock_survey_repo.get_active_survey_for_user.return_value = mock_survey
    mock_survey_res_repo.get_or_create_user_survey_res.return_value = None
    handle_start_use_case = usecases.HandleStartCommandUseCase(
        _user_repo=mock_user_repo,
        _survey_repo=mock_survey_repo,
        _survey_res_repo=mock_survey_res_repo,
        _bot=mock_bot,
    )
    service = StartHandlerService(
        bot=mock_bot, handle_start_use_case=handle_start_use_case
    )

    service(message_with_user)
    mock_survey_repo.get_active_survey_for_user.assert_called_once_with(
        user=mock_user
    )

    mock_survey_res_repo.get_or_create_user_survey_res.assert_called_once_with(
        user=mock_user, survey=mock_survey
    )
    mock_bot.send_message.assert_called_once_with(
        chat_id=message_with_user.chat.id, text='Hello!'
    )


@pytest.mark.parametrize(
    ('input_text', 'expected_id'),
    [
        (f'{START_PREFIX}{SURVEY_KEY}0', 0),
        (f'{START_PREFIX}{SURVEY_KEY}1', 1),
        (f'{START_PREFIX}{SURVEY_KEY}10', 10),
        (f'{START_PREFIX}{SURVEY_KEY}999abrakadabra', 999),
    ],
)
def test_recognize_survey_id_found(input_text: str, expected_id: int) -> None:
    """Test survey key recognized."""
    assert recognize_survey_id(input_text) == expected_id


@pytest.mark.django_db
def test_start_handler_service_with_survey_id(
    department: Department,
    auth_user: CustomUser,
    survey_with_question: Callable[..., tuple[Survey, Question]],
    mock_start_message_with_auth_user: Mock,
) -> None:
    """Test StartHandlerService with real repo methods (no mocks)."""
    user_repo = UserRepo()
    survey_repo = SurveyRepo()
    active_survey, _ = survey_with_question({'department': department})
    mock_start_message_with_auth_user.text = f'/start survey_{active_survey.id}'
    handle_start_use_case = usecases.HandleStartCommandUseCase(
        _user_repo=user_repo,
        _survey_repo=survey_repo,
        _survey_res_repo=SurveyResultRepo(),
        _bot=Mock(),
    )
    service = StartHandlerService(
        bot=Mock(),
        handle_start_use_case=handle_start_use_case,
    )

    service(mock_start_message_with_auth_user)

    assert (
        user_repo.get_by_tg_username(tg_username=auth_user.tg_username)
        == auth_user
    )
    assert (
        survey_repo.get_active_survey_for_user_by_id(
            user=auth_user, survey_id=active_survey.id
        )
        == active_survey
    )
