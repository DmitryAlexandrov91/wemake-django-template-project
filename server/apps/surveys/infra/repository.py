from typing import final

from django.db.models import QuerySet

from server.apps.surveys.models import Question


@final
class QuestionRepo:
    """Repository for Question model operations."""

    def get_all(self) -> QuerySet[Question]:
        """Return all Question instances from DB."""
        return Question.objects.all()

    def get_by_pk(self, pk: int) -> Question:
        """Return one Question by primary key."""
        return Question.objects.get(pk=pk)
