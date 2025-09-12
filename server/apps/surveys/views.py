from typing import override

from django.db.models import QuerySet
from rest_framework.viewsets import ModelViewSet

from server.apps.surveys.models import (
    Survey,
)
from server.apps.surveys.paginators import CustomPaginator
from server.apps.surveys.serializers import SurveyListSerializer
from server.apps.surveys.services import get_modified_surveys_queryset


class SurveyViewSet(ModelViewSet[Survey]):
    """ViewSet for Survey model."""

    serializer_class = SurveyListSerializer
    pagination_class = CustomPaginator

    @override
    def get_queryset(self) -> QuerySet[Survey]:
        """Return modificated Survey`s queryset."""
        return get_modified_surveys_queryset(self.request)
