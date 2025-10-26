from unittest.mock import ANY, MagicMock

import pytest
from django.core.exceptions import ValidationError

from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.tgbot.entrypoints import (
    responses_edit_handler,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    SURVEY_RESULTS_TEMPLATE,
)
from server.apps.users.infra.repository import UserRepo
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_responses_edit_handler(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Ensure responses_edit_handler works correctly."""
    tg_user = user_from_message_with_relations.from_user
    assert tg_user is not None

    user = resolve(UserRepo).get_by_tg_username(f'@{tg_user.username}')

    survey = resolve(SurveyRepo).get_active_survey_for_user(user=user)

    survey_result = resolve(SurveyResultRepo).get_or_create_user_survey_res(
        user=user, survey=survey
    )

    user_answers = resolve(UserAnswerRepo).get_answers_by_survey_result(
        survey_result=survey_result
    )
    responses_edit_handler(message=user_from_message_with_relations)

    mock_bot_send_message.assert_called_once_with(
        chat_id=user_from_message_with_relations.chat.id,
        text=SURVEY_RESULTS_TEMPLATE.format(
            survey_title=survey.title,
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


@pytest.mark.django_db
def test_responses_edit_handler_with_none_user(
    user_from_message_with_relations: MockMessage,
) -> None:
    """Ensure responses_edit_handler raise ValidationError with None user."""
    user_from_message_with_relations.from_user = None

    with pytest.raises(ValidationError):
        responses_edit_handler(message=user_from_message_with_relations)
