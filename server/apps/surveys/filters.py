from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    FilterSet,
)

from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.models.surveys import Survey


class SurveyFilter(FilterSet):
    """Filter surveys."""

    is_favorite = BooleanFilter(
        field_name='is_favorite',
        lookup_expr='exact',
    )
    status = ChoiceFilter(
        field_name='status',
        choices=SurveyStatus.choices,
    )
    department = CharFilter(field_name='department__name', lookup_expr='exact')

    class Meta:
        model = Survey
        fields = ('is_favorite', 'status', 'department')
