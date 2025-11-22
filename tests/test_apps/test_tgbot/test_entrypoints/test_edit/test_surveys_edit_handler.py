from unittest.mock import ANY, MagicMock

import pytest

from server.apps.surveys.infra.repository import (
    SurveyRepo,
)
from server.apps.tgbot.callbacks import survey_list_callback
from server.apps.tgbot.entrypoints.edit import (
    surveys_edit_handler,
)
from server.apps.users.infra.repository import UserRepo
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockCallbackQuery


@pytest.mark.django_db
def test_surveys_edit_handler(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    user_from_message_with_relations: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure that surveys_edit_handler works correctly."""
    tg_user = user_from_message_with_relations.from_user

    user = resolve(UserRepo).get_by_tg_username(f'@{tg_user.username}')
    survey = resolve(SurveyRepo).get_active_survey_for_user(user=user)

    mock_callback_query.data = survey_list_callback.factory.new(
        survey_id=survey.pk, user_id=user.pk
    )

    surveys_edit_handler(mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once_with(
        callback_query_id=mock_callback_query.id
    )
    mock_bot_edit_message_text.assert_called_once_with(
        chat_id=mock_callback_query.message.chat.id,
        message_id=mock_callback_query.message.id,
        text=ANY,
        parse_mode='HTML',
        reply_markup=ANY,
    )


@pytest.mark.django_db
def test_surveys_edit_handler_with_none_call(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure that surveys_edit_handler.

    do nothing without call.data.
    """
    mock_callback_query.data = None
    surveys_edit_handler(mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once_with(
        callback_query_id=mock_callback_query.id
    )
    mock_bot_edit_message_text.assert_not_called()
