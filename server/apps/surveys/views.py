from typing import Any, override

from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.surveys.infra.repository import QuestionRepo
from server.apps.surveys.models import Question, Survey
from server.apps.surveys.paginators import CustomPaginator
from server.apps.surveys.serializers import (
    QuestionCreateSerializer,
    SurveyListSerializer,
)
from server.apps.surveys.services import get_modified_surveys_queryset
from server.di import resolve


class QuestionViewSet(viewsets.ModelViewSet[Question]):
    """ViewSet for managing questions."""

    serializer_class = QuestionCreateSerializer
    http_method_names = ('get', 'post', 'patch')

    @override
    def get_queryset(self) -> QuerySet[Question]:
        """Get queryset using repo."""
        repo = resolve(QuestionRepo)
        return repo.get_all()

    @override
    def partial_update(
        self, request: Request, *args: Any, **kwargs: Any
    ) -> Response:
        """Partial update question using repo."""
        repo = resolve(QuestionRepo)
        qestion = repo.get_by_pk(kwargs['pk'])
        serializer = self.get_serializer(
            qestion, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        upd_qestion = repo.update_question(qestion, **serializer.validated_data)
        return Response(
            self.get_serializer(upd_qestion).data,
            status=status.HTTP_202_ACCEPTED,
        )


class SurveyViewSet(viewsets.ModelViewSet[Survey]):
    """ViewSet for Survey model."""

    serializer_class = SurveyListSerializer
    pagination_class = CustomPaginator

    @override
    def get_queryset(self) -> QuerySet[Survey]:
        """Return modificated Survey`s queryset."""
        return get_modified_surveys_queryset(self.request)
