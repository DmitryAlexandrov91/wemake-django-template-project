from django.db import transaction

from server.apps.surveys.models import Question, SurveyResult


class AdvanceToNextQuestion:
    """Use-case for moving survey forward after answering."""

    @transaction.atomic
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
            Question.objects.filter(
                survey=survey_result.survey,
                id__gt=current_question.id,
            )
            .order_by('id')
            .first()
        )

        survey_result.current_question = next_question
        survey_result.save(update_fields=['current_question'])
        return survey_result
