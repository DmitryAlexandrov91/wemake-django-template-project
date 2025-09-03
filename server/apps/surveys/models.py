from typing import override

from django.db import models

from server.apps.surveys.choices import QuestionType
from server.common.constants import DATA_LENGHT


class Survey(models.Model):
    """Survey model."""

    title = models.CharField(max_length=DATA_LENGHT)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        default_related_name = 'surveys'
        constraints = (
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_dates_valid',
                condition=(
                    models.Q(end_date__gte=models.F('start_date'))
                    | models.Q(end_date__isnull=True)
                ),
            ),
        )

    @override
    def __str__(self) -> str:
        """
        Returns survey title as the object string representation.

        >>> survey = Survey(title='Customer Feedback')
        >>> str(survey) == survey.title
        True

        Constraint check examples:

        >>> from datetime import date
        >>> valid_survey = Survey(
        ...     title='Valid Survey',
        ...     start_date=date(2025, 1, 1),
        ...     end_date=date(2025, 1, 10),
        ... )
        >>> valid_survey.end_date >= valid_survey.start_date
        True

        >>> invalid_survey = Survey(
        ...     title='Invalid Survey',
        ...     start_date=date(2025, 1, 10),
        ...     end_date=date(2025, 1, 1),
        ... )
        >>> invalid_survey.end_date >= invalid_survey.start_date
        False
        """
        return self.title


class Question(models.Model):
    """Question model."""

    survey = models.ForeignKey(
        'surveys.Survey',
        on_delete=models.CASCADE,
        db_index=True,
    )
    text = models.TextField()
    question_type = models.CharField(
        max_length=DATA_LENGHT,
        choices=QuestionType.choices,
    )

    class Meta:
        default_related_name = 'questions'
        constraints = (
            models.UniqueConstraint(
                fields=['survey', 'text'],
                name='unique_question_per_survey',
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_question_type_valid',
                condition=models.Q(question_type__in=QuestionType.values),
            ),
        )

    @override
    def __str__(self) -> str:
        """
        Returns question text as the object string representation.

        >>> survey = Survey(title='Customer Feedback')
        >>> question = Question(survey=survey, text='How old are you?')
        >>> str(question) == question.text
        True
        """
        return self.text


class AnswerOption(models.Model):
    """Model stores predefined choices for multiple-choice questions."""

    question = models.ForeignKey(
        'surveys.Question',
        on_delete=models.CASCADE,
        db_index=True,
    )
    text = models.TextField()

    class Meta:
        verbose_name = 'answer option'
        default_related_name = 'answer_options'
        constraints = (
            models.UniqueConstraint(
                fields=['question', 'text'], name='unique_answer'
            ),
        )

    @override
    def __str__(self) -> str:
        """
        Returns the text of the answer option as its string representation.

        >>> survey = Survey(title='Customer Feedback')
        >>> question = Question(survey=survey, text='Gender?')
        >>> answer_option = AnswerOption(question=question, text='Male')
        >>> str(answer_option) == answer_option.text
        True
        """
        return self.text
