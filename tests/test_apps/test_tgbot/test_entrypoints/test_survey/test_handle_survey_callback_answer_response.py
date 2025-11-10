from unittest.mock import MagicMock

import pytest

from server.apps.surveys.infra.repository import SurveyRepo, SurveyResultRepo
from server.apps.surveys.models.surveys import UserAnswer
from server.apps.tgbot.callbacks import survey_callback
from server.apps.tgbot.entrypoints.survey import (
    handle_survey_callback_answer_response,
)
from server.apps.users.infra.repository import UserRepo
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockCallbackQuery, MockMessage


@pytest.mark.django_db
def test_handle_survey_callback_answer_response(
    user_from_message_with_relations: MockMessage,
    mock_bot_edit_message_text: MagicMock,
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
) -> None:
    """Ensure handle_survey_callback_answer_response works correctly."""
    tg_user = user_from_message_with_relations.from_user
    assert tg_user is not None

    answer_to_question = 'Answer to question from callback'

    user = resolve(UserRepo).get_by_tg_username(f'@{tg_user.username}')
    survey_result = resolve(SurveyResultRepo).get_or_create_user_survey_res(
        user=user,
        survey=resolve(SurveyRepo).get_active_survey_for_user(user=user),
    )

    mock_callback_query.data = survey_callback.factory.new(
        survey_result_id=survey_result.pk,
        question_id=survey_result.current_question.pk,  # type: ignore[union-attr]
        answer_option=answer_to_question,
    )

    handle_survey_callback_answer_response(call=mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once()
    mock_bot_edit_message_text.assert_called_once()
    assert UserAnswer.objects.filter(
        survey_result=survey_result, text_answer=answer_to_question
    ).exists()


@pytest.mark.django_db
def test_handle_survey_callback_with_non_call(
    mock_bot_edit_message_text: MagicMock,
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
) -> None:
    """Ensure handle_survey_callback returns early when call.data is None."""
    mock_callback_query.data = None

    handle_survey_callback_answer_response(call=mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once()
    mock_bot_edit_message_text.assert_not_called()
