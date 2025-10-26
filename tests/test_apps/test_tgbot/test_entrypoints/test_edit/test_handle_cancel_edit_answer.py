from unittest.mock import ANY, MagicMock

import pytest
from django.db import models

from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import SurveyResult, UserAnswer
from server.apps.tgbot.callbacks import answer_cancel_callback
from server.apps.tgbot.entrypoints import (
    handle_cancel_edit_answer,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    SURVEY_RESULTS_TEMPLATE,
)
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockCallbackQuery


@pytest.mark.django_db
def test_handle_cancel_edit_answer(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    fakery_m: FakeryM[models.Model],
) -> None:
    """Ensure that handle_cancel_edit_answer works correctly."""
    survey_result = fakery_m(SurveyResult)()
    batch = 3
    for _ in range(batch):
        fakery_m(UserAnswer)(survey_result=survey_result)

    mock_callback_query.data = answer_cancel_callback.factory.new(
        answer_id=1, survey_result_id=survey_result.pk
    )
    user_answers = resolve(UserAnswerRepo).get_answers_by_survey_result(
        survey_result=survey_result  # type: ignore [arg-type]
    )
    handle_cancel_edit_answer(call=mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once_with(
        mock_callback_query.id
    )
    mock_bot_edit_message_text.assert_called_once_with(
        chat_id=mock_callback_query.message.chat.id,
        message_id=mock_callback_query.message.message_id,
        text=SURVEY_RESULTS_TEMPLATE.format(
            survey_title=survey_result.survey.title,  # type: ignore [attr-defined]
            answers=''.join(
                ANSWER_TEMPLATE.format(
                    question_number=answer.pk,
                    question_text=answer.question,
                    answer_text=answer.text_answer,
                )
                for answer in user_answers
            ),
        ),
        parse_mode='HTML',
        reply_markup=ANY,
    )


def test_handle_cancel_edit_answer_with_none_data(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure that handle_cancel_edit_answer do nothing without call.data."""
    mock_callback_query.data = None
    handle_cancel_edit_answer(call=mock_callback_query)
    mock_bot_edit_message_text.assert_not_called()
