from typing import override

from django.db import models

from server.apps.surveys.choices import QuestionType
from server.common.constants import DATA_LENGHT


class Question(models.Model):
    """Question model."""

    text = models.TextField()
    question_type = models.CharField(
        max_length=DATA_LENGHT,
        choices=QuestionType.choices,
    )

    class Meta:
        default_related_name = 'question'
        constraints = (
            models.UniqueConstraint(fields=['text'], name='unique_question'),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_question_type_valid',
                condition=models.Q(question_type__in=QuestionType.values),
            ),
        )

    @override
    def __str__(self) -> str:
        """
        Returns question text as the object string representation.

        >>> question = Question(text='AnyText')
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
        default_related_name = 'answeroption'
        constraints = (
            models.UniqueConstraint(
                fields=['question', 'text'], name='unique_answer'
            ),
        )

    @override
    def __str__(self) -> str:
        """
        Returns the text of the answer option as its string representation.

        >>> question = Question(text='AnyText')
        >>> answer_option = AnswerOption(question=question, text='Answer')
        >>> str(answer_option) == answer_option.text
        True
        """
        return self.text
