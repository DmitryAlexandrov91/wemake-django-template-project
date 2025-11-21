from unittest.mock import MagicMock

import pytest
from telebot import TeleBot

from server.apps.surveys.infra.repository import SurveyRepo, SurveyResultRepo
from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.entrypoints.survey import survey_handler
from server.apps.tgbot.message_templates import SURVEY_COMPLITED
from server.apps.users.infra.repository import UserRepo
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_survey_handler(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
    mock_bot_delete_state: MagicMock,
) -> None:
    """Ensure survey_handler works correctly."""
    bot = resolve(TeleBot)

    tg_user = user_from_message_with_relations.from_user
    user_from_message_with_relations.text = '/survey'
    assert tg_user is not None

    bot.set_state(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
        state='response_state',
    )

    survey_handler(
        message=user_from_message_with_relations,
        survey_result=SurveyResult.objects.first(),
    )
    mock_bot_delete_state.assert_not_called()
    mock_bot_send_message.assert_called_once()


@pytest.mark.django_db
def test_survey_handler_with_none_user(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
    mock_bot_delete_state: MagicMock,
) -> None:
    """Ensure survey_handler returns early when from_user is None."""
    user_from_message_with_relations.from_user = None
    user_from_message_with_relations.text = '/survey'

    survey_handler(
        message=user_from_message_with_relations,
        survey_result=SurveyResult.objects.first(),
    )

    mock_bot_delete_state.assert_not_called()
    mock_bot_send_message.assert_not_called()


@pytest.mark.django_db
def test_survey_handler_with_none_question(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
    mock_delete_state: MagicMock,
) -> None:
    """Ensure survey_handler delete state when current_question is None."""
    tg_user = user_from_message_with_relations.from_user
    user_from_message_with_relations.text = '/survey'
    assert tg_user is not None

    user = resolve(UserRepo).get_by_tg_username(f'@{tg_user.username}')
    survey = resolve(SurveyRepo).get_active_survey_for_user(user=user)
    survey_result = resolve(SurveyResultRepo).get_or_create_user_survey_res(
        user=user, survey=survey
    )
    survey_result.current_question = None
    survey_result.save(update_fields=['current_question'])
    survey_result.refresh_from_db()
    assert survey_result.current_question is None

    survey_handler(
        message=user_from_message_with_relations, survey_result=survey_result
    )
    mock_delete_state.assert_called_once_with(
        user_id=tg_user.id, chat_id=user_from_message_with_relations.chat.id
    )
    mock_bot_send_message.assert_called_once_with(
        chat_id=user_from_message_with_relations.chat.id,
        text=SURVEY_COMPLITED,
        parse_mode='HTML',
        reply_markup=None,
    )
