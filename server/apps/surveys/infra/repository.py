from server.apps.surveys.models import AnswerOption


class AnswerOptionRepo:
    """Repository for AnswerOption model."""

    def __init__(self, model: type[AnswerOption] = AnswerOption):
        """Initialize repository."""
        self.model = model

    def get_all(self) -> list[AnswerOption]:
        """Returns all answer options from DB."""
        return list(self.model.objects.all())

    def get_by_pk(self, pk: int) -> AnswerOption | None:
        """Returns one answer option from DB by pk."""
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None
