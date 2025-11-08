from unittest.mock import MagicMock

import pytest
from telebot import TeleBot

from server.apps.surveys.models import UserAnswer
from server.apps.tgbot.entrypoints.edit_answers import handle_new_answer_text
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockCallbackQuery, MockMessage


@pytest.mark.django_db
def test_handle_new_answer_text(
    user_from_message_with_relations: MockMessage,
    mock_bot_delete_message: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    mock_callback_query: MockCallbackQuery,
) -> None:
    """Ensure that handle_new_answer_text works correctly."""
    bot = resolve(TeleBot)

    user_answer = UserAnswer.objects.first()
    assert user_answer is not None

    user_from_message_with_relations.text = 'New answer text'

    bot.set_state(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
        state='editing_answer',
    )
    with bot.retrieve_data(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
    ) as state_data:
        state_data['answer_id'] = user_answer.pk
        state_data['survey_result_id'] = user_answer.survey_result.pk
        state_data['callback_id'] = mock_callback_query.id

    handle_new_answer_text(message=user_from_message_with_relations)

    mock_bot_delete_message.assert_called_once_with(
        chat_id=user_from_message_with_relations.chat.id,
        message_id=user_from_message_with_relations.id,
    )

    mock_bot_edit_message_text.assert_called_once()
    call_kwargs = mock_bot_edit_message_text.call_args.kwargs
    assert call_kwargs['chat_id'] == user_from_message_with_relations.chat.id
    assert call_kwargs['message_id'] == mock_callback_query.id
    assert call_kwargs['parse_mode'] == 'HTML'

    user_answer.refresh_from_db()
    assert user_answer.text_answer == 'New answer text'


@pytest.mark.django_db
def test_handle_new_answer_text_with_none_user(
    user_from_message_with_relations: MockMessage,
    mock_bot_delete_message: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    mock_callback_query: MockCallbackQuery,
) -> None:
    """Ensure handle_new_answer_text returns early when from_user is None."""
    bot = resolve(TeleBot)

    user_answer = UserAnswer.objects.first()
    assert user_answer is not None

    bot.set_state(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
        state='editing_answer',
    )
    with bot.retrieve_data(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
    ) as state_data:
        state_data['answer_id'] = user_answer.pk
        state_data['survey_result_id'] = user_answer.survey_result.pk
        state_data['callback_id'] = mock_callback_query.id

    user_from_message_with_relations.from_user = None

    handle_new_answer_text(message=user_from_message_with_relations)
    mock_bot_delete_message.assert_called_once()
    mock_bot_edit_message_text.assert_not_called()


@pytest.mark.django_db
def test_handle_new_answer_text_with_none_text(
    user_from_message_with_relations: MockMessage,
    mock_bot_delete_message: MagicMock,
    mock_bot_edit_message_text: MagicMock,
    mock_callback_query: MockCallbackQuery,
) -> None:
    """Ensure handle_new_answer_text returns early when text is None."""
    bot = resolve(TeleBot)

    user_answer = UserAnswer.objects.first()
    assert user_answer is not None

    bot.set_state(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
        state='editing_answer',
    )
    with bot.retrieve_data(
        user_id=user_from_message_with_relations.from_user.id,  # type: ignore[union-attr]
        chat_id=user_from_message_with_relations.chat.id,
    ) as state_data:
        state_data['answer_id'] = user_answer.pk
        state_data['survey_result_id'] = user_answer.survey_result.pk
        state_data['callback_id'] = mock_callback_query.id

    user_from_message_with_relations.text = None

    handle_new_answer_text(message=user_from_message_with_relations)

    mock_bot_delete_message.assert_called_once()
    mock_bot_edit_message_text.assert_not_called()
