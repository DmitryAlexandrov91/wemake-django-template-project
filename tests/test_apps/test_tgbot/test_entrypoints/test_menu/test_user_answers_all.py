from unittest.mock import MagicMock

import pytest

from server.apps.surveys.choices import SurveyBotState
from server.apps.surveys.infra.repository import SurveyResultRepo
from server.apps.tgbot.entrypoints.menu import handle_show_archive_answers
from server.apps.tgbot.logic.menu.constants import MESSAGE_NO_ANSWER
from server.apps.tgbot.logic.menu.services import generate_view_answers_message
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import SurveyResultFactory
from tests.plugins.tgbot.fixtures import MockCallbackQuery

CHAT_ID_FIELD = 'chat_id'
TEXT_FIELD = 'text'


@pytest.mark.django_db
def test_show_all_archive_answers_callback(
    mock_callback_query: MockCallbackQuery,
    auth_user: CustomUser,
    mock_bot_send_message: MagicMock,
    surveys_survey_result_factory: SurveyResultFactory,
    mock_bot_answer_callback_query: MagicMock,
) -> None:
    """Test that 'show_all_archive_answers' callback sends correct messages."""
    mock_callback_query.from_user.username = auth_user.tg_username.lstrip('@')
    surveys_survey_result_factory(
        user=auth_user, bot_state=SurveyBotState.COMPLETED
    )
    survey_results = resolve(SurveyResultRepo).get_completed_surveys(auth_user)
    handle_show_archive_answers(mock_callback_query)

    mock_bot_send_message.assert_called_once()
    message_template = generate_view_answers_message(survey_results)
    args = mock_bot_send_message.call_args.kwargs
    assert args[CHAT_ID_FIELD] == mock_callback_query.message.chat.id
    assert args[TEXT_FIELD] == message_template


@pytest.mark.django_db
def test_no_results_sends_no_answer(
    mock_callback_query: MockCallbackQuery,
    auth_user: CustomUser,
    mock_bot_send_message: MagicMock,
    mock_bot_answer_callback_query: MagicMock,
) -> None:
    """Test absence of survey results."""
    mock_callback_query.from_user.username = auth_user.tg_username.lstrip('@')
    handle_show_archive_answers(mock_callback_query)
    mock_bot_send_message.assert_called_once()
    args = mock_bot_send_message.call_args.kwargs
    assert args[CHAT_ID_FIELD] == mock_callback_query.message.chat.id
    assert args[TEXT_FIELD] == MESSAGE_NO_ANSWER
