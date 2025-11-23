from typing import final

from server.apps.surveys.models import SurveyQuestion
from server.apps.surveys.models.surveys import Question, Survey


@final
class SurveyQuestionRepo:
    """Repository for SurveyQuestion model."""

    def get_survey_question_next_question(
        self,
        survey: Survey,
        current_question: Question,
    ) -> Question | None:
        """
        Returns SurveyQuestion next question or None.

        by survey and current question.
        """
        survey_question = SurveyQuestion.objects.get(
            survey=survey, question=current_question
        )
        next_survey_question = (
            SurveyQuestion.objects.filter(
                survey=survey, pk__gt=survey_question.pk
            )
            .order_by('pk')
            .first()
        )

        return next_survey_question.question if next_survey_question else None
