from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.db import transaction

from server.apps.surveys.choices import SurveyBotState
from server.apps.surveys.infra.survey_question_repo import SurveyQuestionRepo
from server.apps.surveys.models import SurveyResult

if TYPE_CHECKING:
    from server.apps.surveys.usecases.statistics_services import (
        UpdateStatisticScheduler,
    )


@dataclass(frozen=True)
class AdvanceToNextQuestion:
    """Use-case for moving survey forward after answering."""

    _sheduler: UpdateStatisticScheduler
    _survey_question_repo: SurveyQuestionRepo

    def __call__(self, survey_result: SurveyResult) -> SurveyResult:
        """
        Advance the given survey result to the next question.

        If the current question is the last one, set current_question to None,
        effectively marking the survey as completed.

        Args:
            survey_result (SurveyResult): The survey result to update.

        Returns:
            SurveyResult: The updated survey result instance.
        """
        current_question = survey_result.current_question
        if not current_question:
            return survey_result

        next_question = (
            self._survey_question_repo.get_survey_question_next_question(
                current_question=current_question, survey=survey_result.survey
            )
        )

        is_completed = (
            not next_question and survey_result.completed_questions > 0
        )

        with transaction.atomic():
            survey_result.current_question = next_question
            survey_result.completed_questions += 1
            updated_fields = [
                'current_question',
                'completed_questions',
                'updated_at',
            ]

            if is_completed:
                survey_result.bot_state = SurveyBotState.COMPLETED
                updated_fields.append('bot_state')

            survey_result.save(update_fields=updated_fields)

        if is_completed:
            self._sheduler(user_id=survey_result.user.pk)

        return survey_result
