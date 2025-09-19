from typing import Any, override

from django.db.models import QuerySet
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.surveys.infra.repository import QuestionRepo, SurveyRepo
from server.apps.surveys.models import Question, Survey
from server.apps.surveys.paginators import CustomPaginator
from server.apps.surveys.serializers_create import (
    QuestionCreateSerializer,
    SurveyCreateSerializer,
    SurveyUpdateSerializer,
)
from server.apps.surveys.serializers_list import (
    QuestionShortSerializer,
    SurveyListSerializer,
)
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

    pagination_class = CustomPaginator
    http_method_names = ('get', 'post', 'patch')

    @override
    def get_serializer_class(
        self,
    ) -> type[serializers.BaseSerializer[Survey]]:
        """Method for selecting serializer."""
        return {
            'create': SurveyCreateSerializer,
            'partial_update': SurveyUpdateSerializer,
        }.get(self.action, SurveyListSerializer)

    @override
    def get_queryset(self) -> QuerySet[Survey]:
        """Return modificated Survey`s queryset."""
        return resolve(SurveyRepo).get_modified_surveys_queryset(self.request)

    @override
    def create(
        self,
        request: Request,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],  # noqa: WPS221
    ) -> Response:
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        return Response(
            SurveyListSerializer(
                resolve(SurveyRepo).build_survey_for_create_response(
                    create_serializer.save(),
                ),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @override
    def partial_update(
        self, request: Request, *args: Any, **kwargs: Any
    ) -> Response:
        """Partial update survey using repo."""
        repo = resolve(SurveyRepo)
        survey = repo.get_modified_surveys_queryset(request).get(
            pk=kwargs['pk']
        )
        serializer = self.get_serializer(
            survey,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated_survey = repo.update_survey(survey, **serializer.validated_data)

        return Response(
            SurveyListSerializer(updated_survey).data,
            status=status.HTTP_202_ACCEPTED,
        )


class QuestionListViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet[Question]
):
    """ViewSet for Question model."""

    serializer_class = QuestionShortSerializer
    pagination_class = CustomPaginator

    @override
    def get_queryset(self) -> QuerySet[Question]:
        """Return modificated Survey`s queryset."""
        return resolve(QuestionRepo).get_modified_questions_queryset(
            self.request
        )
