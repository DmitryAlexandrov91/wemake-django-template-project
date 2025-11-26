from typing import Any, override

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    mixins,
    request,
    response,
    serializers,
    status,
    viewsets,
)

from server.apps.surveys import choices, filters, models, paginators
from server.apps.surveys.infra.repository import (
    QuestionRepo,
    SurveyRepo,
    SurveySaveRepo,
)
from server.apps.surveys.schemas import question_viewset_schema
from server.apps.surveys.serializers_create import (
    QuestionCreateSerializer,
    SurveyCreateSerializer,
    SurveyUpdateSerializer,
)
from server.apps.surveys.serializers_list import (
    QuestionShortSerializer,
    SurveyListSerializer,
)
from server.apps.surveys.usecases.inform_recipients import survey_notification
from server.di import resolve

ALL_PARAM = 'all'
DEFAULT_ORDER = 'desc'
DETAIL_KEY = 'detail'


@question_viewset_schema
class QuestionViewSet(  # noqa: WPS215
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[models.Question],
):
    """ViewSet for managing questions."""

    serializer_class = QuestionCreateSerializer
    pagination_class = paginators.CustomPaginator
    http_method_names = ('get', 'post', 'patch', 'delete')

    @override
    def get_queryset(self) -> QuerySet[models.Question]:
        """Get queryset using repo."""
        repo = resolve(QuestionRepo)
        filter_param = self.request.query_params.get('filter', ALL_PARAM)
        order_param = self.request.query_params.get('order', DEFAULT_ORDER)
        search_param = self.request.query_params.get('search')
        return repo.get_modified_questions_queryset(
            filter_param, order_param, search_param
        )

    @override
    def get_serializer_class(  # noqa: WPS615
        self,
    ) -> type[serializers.BaseSerializer[models.Question]]:
        """Return serializer class depending on action."""
        if self.action == 'list':
            return QuestionShortSerializer
        return super().get_serializer_class()

    @override
    def partial_update(
        self, request: request.Request, *args: Any, **kwargs: Any
    ) -> response.Response:
        """Partial update question using repo."""
        if not request.data:
            return response.Response(
                {DETAIL_KEY: 'PATCH request body cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        repo = resolve(QuestionRepo)
        qestion = repo.get_by_pk(kwargs['pk'])
        serializer = self.get_serializer(
            qestion, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        upd_qestion = repo.update_question(qestion, **serializer.validated_data)
        return response.Response(
            self.get_serializer(upd_qestion).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @override
    def destroy(self, request: request.Request, pk: int) -> response.Response:
        """Mark question for deletion by primary key."""
        repo = resolve(QuestionRepo)
        question = repo.get_by_pk(pk=pk)
        if repo.survey_assigned_to_question(question):
            return response.Response(
                data={'error': 'Survey(s) assigned to the question.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        repo.update_question(question=question, to_delete=True)
        return response.Response(status=status.HTTP_200_OK)


class SurveyViewSet(viewsets.ModelViewSet[models.Survey]):
    """ViewSet for Survey model."""

    pagination_class = paginators.CustomPaginator
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SurveyFilter

    @override
    def get_serializer_class(
        self,
    ) -> type[serializers.BaseSerializer[models.Survey]]:
        """Method for selecting serializer."""
        return {
            'create': SurveyCreateSerializer,
            'partial_update': SurveyUpdateSerializer,
        }.get(self.action, SurveyListSerializer)

    @override
    def get_object(self) -> models.Survey:
        return (
            resolve(SurveyRepo)
            .get_modified_surveys_queryset(self.request)
            .get(pk=self.kwargs['pk'])
        )

    @override
    def get_queryset(self) -> QuerySet[models.Survey]:
        """Return modificated Survey`s queryset."""
        return resolve(SurveyRepo).get_modified_surveys_queryset(self.request)

    @override
    def create(
        self,
        request: request.Request,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],  # noqa: WPS221
    ) -> response.Response:
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        try:
            created_survey = create_serializer.save()
        except models.Question.DoesNotExist:
            return response.Response(
                {DETAIL_KEY: 'Передан несуществующий вопрос'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return response.Response(
            SurveyListSerializer(
                resolve(SurveyRepo).build_survey_for_create_response(
                    created_survey
                )
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @override
    def partial_update(
        self, request: request.Request, *args: Any, **kwargs: Any
    ) -> response.Response:
        """Partial update survey using repo."""
        if not request.data:
            return response.Response(
                {DETAIL_KEY: 'PATCH request body cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        survey = self.get_object()
        survey_status_orig = survey.status
        serializer = self.get_serializer(
            survey,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_survey = resolve(SurveyRepo).update_survey(
                survey, **serializer.validated_data
            )
        except models.Question.DoesNotExist:
            return response.Response(
                {DETAIL_KEY: 'Передан несуществующий вопрос'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            survey_status_orig == choices.SurveyStatus.DRAFT
            and updated_survey.status == choices.SurveyStatus.ACTIVE
        ):
            survey_notification(survey=updated_survey)

        return response.Response(
            SurveyListSerializer(updated_survey).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @override
    def destroy(self, request: request.Request, pk: int) -> response.Response:
        """Mark survey for deletion by primary key."""
        survey = resolve(SurveySaveRepo).get_by_pk(pk)
        resolve(SurveyRepo).update_survey(survey=survey, to_delete=True)
        return response.Response(status=status.HTTP_200_OK)
