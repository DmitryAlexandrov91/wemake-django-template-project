from typing import Any, override

from django.core.exceptions import ValidationError
from django.db import models

from server.apps.surveys.choices import (
    QuestionType,
    SurveyBotState,
    SurveyStatus,
)
from server.common.constants import DATA_LENGHT


class Survey(models.Model):
    """Survey model."""

    title = models.CharField(max_length=DATA_LENGHT)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        to='company.Department',
        on_delete=models.CASCADE,
        related_name='surveys',
    )
    is_favorite = models.BooleanField(default=False)
    to_delete = models.BooleanField(default=0)

    status = models.CharField(
        max_length=DATA_LENGHT,
        choices=SurveyStatus.choices,
        default=SurveyStatus.DRAFT,
    )

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
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_status_valid',
                condition=(models.Q(status__in=SurveyStatus.values)),
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

    surveys = models.ManyToManyField(  # type: ignore[var-annotated]
        'surveys.Survey',
        related_name='questions',
        through='SurveyQuestion',
    )
    text = models.TextField()
    question_type = models.CharField(
        max_length=DATA_LENGHT,
        choices=QuestionType.choices,
    )
    is_favorite = models.BooleanField(default=False)
    to_delete = models.BooleanField(default=0)

    class Meta:
        ordering = ('id',)
        default_related_name = 'questions'
        constraints = (
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
        >>> question = Question(text='How old are you?')
        >>> str(question) == question.text
        True
        """
        return self.text


class SurveyQuestion(models.Model):
    """Link between survey and question."""

    survey = models.ForeignKey(
        'surveys.Survey', on_delete=models.CASCADE, db_index=True
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, db_index=True
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['survey', 'question'], name='unique_survey_question'
            ),
        )

    @override
    def clean(self) -> None:
        """Ensure unique text in survey."""
        if (
            SurveyQuestion.objects.filter(
                survey=self.survey, question__text=self.question.text
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                'This survey already has a question with this text.'
            )

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save."""
        self.clean()
        super().save(*args, **kwargs)


class AnswerOption(models.Model):
    """Model stores predefined choices for multiple-choice questions."""

    question = models.ForeignKey(
        'surveys.Question',
        on_delete=models.CASCADE,
        db_index=True,
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

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
        >>> question = Question(text='Gender?')
        >>> answer_option = AnswerOption(question=question, text='Male')
        >>> str(answer_option) == answer_option.text
        True
        """
        return self.text


class SurveyResult(models.Model):
    """Survey result model."""

    user = models.ForeignKey(
        to='users.CustomUser',
        on_delete=models.CASCADE,
        related_name='survey_result',
    )
    survey = models.ForeignKey(
        to='surveys.Survey',
        on_delete=models.CASCADE,
        related_name='result',
    )
    current_question = models.ForeignKey(
        to='surveys.Question',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    completed_questions = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot_state = models.CharField(
        max_length=DATA_LENGHT,
        choices=SurveyBotState.choices,
        default=SurveyBotState.WAITING_START,
    )

    class Meta:
        verbose_name = 'survey result'
        verbose_name_plural = 'survey results'
        constraints = (
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_bot_state_valid',
                condition=(models.Q(bot_state__in=SurveyBotState.values)),
            ),
        )

    @override
    def __str__(self) -> str:
        """
        Returns the SurveyResult object string representation.

        >>> from server.apps.users.models import CustomUser
        >>> user = CustomUser(
        ...     email='test@example.com',
        ...     full_name='test_name',
        ... )
        >>> survey = Survey(title='Customer Feedback')
        >>> survey_result = SurveyResult(
        ...     user=user,
        ...     survey=survey,
        ... )
        >>> str(survey_result) == f'Result {user} for survey id={survey.id}'
        True
        """
        return f'Result {self.user} for survey id={self.survey_id}'


class UserAnswer(models.Model):
    """User answer model."""

    survey_result = models.ForeignKey(
        to='surveys.SurveyResult',
        on_delete=models.CASCADE,
        related_name='user_answers',
    )
    question = models.ForeignKey(
        to='surveys.Question',
        on_delete=models.CASCADE,
        related_name='user_answers',
    )

    text_answer = models.TextField(
        blank=True,
    )

    selected_options = models.ManyToManyField(
        to='surveys.AnswerOption',
        related_name='user_answers',
        blank=True,
    )

    class Meta:
        verbose_name = 'user answer'
        verbose_name_plural = 'user answers'

    @override
    def __str__(self) -> str:
        """
        Returns the UserAnswer object string representation.

        >>> from server.apps.users.models import CustomUser
        >>> user = CustomUser(
        ...     email='test@example.com',
        ...     full_name='test_name',
        ... )
        >>> survey = Survey(title='Customer Feedback')
        >>> survey_result = SurveyResult(
        ...     user=user,
        ...     survey=survey,
        ... )
        >>> question = Question(text='Gender?')
        >>> user_answer = UserAnswer(
        ...     survey_result=survey_result,
        ...     question=question,
        ...     text_answer='Some answer',
        ... )
        >>> str(user_answer) == user_answer.text_answer
        True
        """
        return self.text_answer


class Suggestion(models.Model):
    """Suggestion model."""

    user = models.ForeignKey(
        to='users.CustomUser',
        on_delete=models.CASCADE,
        related_name='suggestions',
    )
    title = models.CharField()
    description = models.TextField()

    class Meta:
        verbose_name = 'suggestion'
        verbose_name_plural = 'suggestions'

    @override
    def __str__(self) -> str:
        """
        Returns the UserAnswer object string representation.

        >>> from server.apps.users.models import CustomUser
        >>> user = CustomUser(
        ...     email='test@example.com',
        ...     full_name='test_name',
        ... )
        >>> user_suggestion = Suggestion(
        ...     user=user,
        ...     title='Suggestion title',
        ...     description='Suggestion description',
        ... )
        >>> str(user_suggestion) == user_suggestion.title
        True
        """
        return self.title
