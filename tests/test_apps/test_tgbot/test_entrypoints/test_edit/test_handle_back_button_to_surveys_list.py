from unittest.mock import ANY, MagicMock

import pytest

from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.callbacks import back_to_active_surveys
from server.apps.tgbot.entrypoints.edit import (
    handle_back_button_to_surveys_list,
)
from server.apps.tgbot.message_templates import SURVEY_CHOISE
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockCallbackQuery


@pytest.mark.django_db
def test_handle_back_button(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    fakery_m: FakeryM[SurveyResult],
) -> None:
    """Ensure that handle_back_button_to_surveys_list works correctly."""
    survey_result = fakery_m(SurveyResult)()

    mock_callback_query.data = back_to_active_surveys.factory.new(
        survey_result_id=survey_result.pk
    )

    handle_back_button_to_surveys_list(mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once_with(
        callback_query_id=mock_callback_query.id
    )
    mock_bot_edit_message_text.assert_called_once_with(
        chat_id=mock_callback_query.message.chat.id,
        message_id=mock_callback_query.message.id,
        text=SURVEY_CHOISE,
        reply_markup=ANY,
    )


@pytest.mark.django_db
def test_handle_back_button_with_none_call(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure that handle_back_button_to_surveys_list.

    do nothing without call.data.
    """
    mock_callback_query.data = None
    handle_back_button_to_surveys_list(mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once_with(
        callback_query_id=mock_callback_query.id
    )
    mock_bot_edit_message_text.assert_not_called()
