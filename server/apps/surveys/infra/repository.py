from typing import Any, final

from django.db.models import QuerySet

from server.apps.surveys.models import AnswerOption, Question


@final
class AnswerOptionRepo:
    """Repository for AnswerOption model."""

    def get_all(self) -> QuerySet[AnswerOption]:
        """Returns all answer options from DB."""
        return AnswerOption.objects.select_related('question')

    def get_by_pk(self, pk: int) -> AnswerOption:
        """Returns one answer option from DB by pk."""
        return AnswerOption.objects.select_related('question').get(pk=pk)


@final
class QuestionRepo:
    """Repository for Question model operations."""

    def get_all(self) -> QuerySet[Question]:
        """Return all Question instances from DB."""
        return Question.objects.select_related('survey', 'survey__department')

    def get_by_pk(self, pk: int) -> Question:
        """Return one Question by primary key."""
        return self.get_all().get(pk=pk)

    def update_question(self, question: Question, **kwargs: Any) -> Question:
        """Update an existing question."""
        Question.objects.filter(pk=question.pk).update(**kwargs)
        question.refresh_from_db()
        return question
