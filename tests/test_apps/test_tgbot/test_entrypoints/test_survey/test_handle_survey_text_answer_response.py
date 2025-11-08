from unittest.mock import MagicMock

import pytest
from telebot import TeleBot

from server.apps.surveys.infra.repository import SurveyRepo, SurveyResultRepo
from server.apps.surveys.models.surveys import Question, SurveyResult
from server.apps.tgbot.entrypoints.survey import (
    handle_survey_text_answer_response,
)
from server.apps.tgbot.message_templates import SURVEY_COMPLITED
from server.apps.users.infra.repository import UserRepo
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_handle_survey_text_answer_response(
    user_from_message_with_relations: MockMessage,
    mock_bot_delete_message: MagicMock,
    mock_bot_delete_state: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure handle_survey_text_answer_response works correctly."""
    bot = resolve(TeleBot)

    tg_user = user_from_message_with_relations.from_user
    user_from_message_with_relations.text = 'New answer for question'
    assert tg_user is not None

    survey_result = SurveyResult.objects.first()

    bot.set_state(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
        state='response_state',
    )

    with bot.retrieve_data(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
    ) as state_data:
        state_data['survey_result_id'] = survey_result.pk  # type: ignore[union-attr]
        state_data['question_id'] = survey_result.current_question.pk  # type: ignore[union-attr]
        state_data['message_id'] = user_from_message_with_relations.message_id

    handle_survey_text_answer_response(message=user_from_message_with_relations)
    mock_bot_delete_message.assert_called_once()
    mock_bot_delete_state.assert_not_called()
    mock_bot_edit_message_text.assert_called_once()


@pytest.mark.django_db
def test_handle_survey_text_with_none_user(
    user_from_message_with_relations: MockMessage,
    mock_bot_delete_state: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    mock_bot_delete_message: MagicMock,
) -> None:
    """Ensure handle_survey returns early when from_user is None."""
    user_from_message_with_relations.from_user = None
    user_from_message_with_relations.text = '/survey'

    handle_survey_text_answer_response(message=user_from_message_with_relations)
    mock_bot_delete_message.assert_called_once()
    mock_bot_delete_state.assert_not_called()
    mock_bot_edit_message_text.assert_not_called()


@pytest.mark.django_db
def test_handle_survey_text_with_none_question(
    user_from_message_with_relations: MockMessage,
    mock_bot_delete_state: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    mock_bot_delete_message: MagicMock,
) -> None:
    """Ensure handle_survey delete state when current_question is None."""
    bot = resolve(TeleBot)

    tg_user = user_from_message_with_relations.from_user
    user_from_message_with_relations.text = 'New answer for question'
    assert tg_user is not None

    user = resolve(UserRepo).get_by_tg_username(f'@{tg_user.username}')
    survey_result = resolve(SurveyResultRepo).get_or_create_user_survey_res(
        user=user,
        survey=resolve(SurveyRepo).get_active_survey_for_user(user=user),
    )
    survey_result.current_question = None
    survey_result.save(update_fields=['current_question'])
    survey_result.refresh_from_db()
    assert survey_result.current_question is None

    bot.set_state(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
        state='response_state',
    )

    with bot.retrieve_data(  # type: ignore[union-attr]
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
    ) as state_data:
        state_data['survey_result_id'] = survey_result.pk
        state_data['question_id'] = Question.objects.first().pk  # type: ignore[union-attr]
        state_data['message_id'] = user_from_message_with_relations.message_id

    handle_survey_text_answer_response(message=user_from_message_with_relations)
    mock_bot_delete_state.assert_called_once_with(
        user_id=tg_user.id, chat_id=user_from_message_with_relations.chat.id
    )
    mock_bot_edit_message_text.assert_called_once_with(
        chat_id=user_from_message_with_relations.chat.id,
        text=SURVEY_COMPLITED,
        parse_mode='HTML',
        reply_markup=None,
        message_id=user_from_message_with_relations.message_id,
    )
