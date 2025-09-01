from typing import final

from django.db.models import QuerySet

from server.apps.surveys.models import AnswerOption, Question


@final
class AnswerOptionRepo:
    """Repository for AnswerOption model."""

    def __init__(self, model: type[AnswerOption] = AnswerOption):
        """Initialize repository."""
        self.model = model

    def get_all(self) -> QuerySet[AnswerOption]:
        """Returns all answer options from DB."""
        return self.model.objects.all()

    def get_by_pk(self, pk: int) -> AnswerOption | None:
        """Returns one answer option from DB by pk."""
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None


@final
class QuestionRepo:
    """Repository for Question model operations."""

    def get_all(self) -> QuerySet[Question]:
        """Return all Question instances from DB."""
        return Question.objects.all()

    def get_by_pk(self, pk: int) -> Question:
        """Return one Question by primary key."""
        return Question.objects.get(pk=pk)
