from types import MappingProxyType
from typing import Any

from django.db import models
from django.utils import timezone
from django_filters.rest_framework import CharFilter, FilterSet

from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.models.surveys import Survey

STATUS_MAPPING: MappingProxyType[str, dict[str, Any]] = MappingProxyType({
    'favorite': {'is_favorite': True},
    'drafts': {'status': SurveyStatus.DRAFT},
    'archive': {'status': SurveyStatus.ARCHIVED},
})


class SurveyFilter(FilterSet):
    """Filter surveys."""

    status = CharFilter(method='filter_status')
    department = CharFilter(field_name='department__name', lookup_expr='exact')

    class Meta:
        model = Survey
        fields = ('status', 'department')

    def filter_status(
        self,
        queryset: models.QuerySet[Survey],
        name: str,
        filter_value: str,
    ) -> models.QuerySet[Survey]:
        """Status filters some fields."""
        now_date = timezone.now().date()
        if filter_value in STATUS_MAPPING:
            queryset = queryset.filter(**STATUS_MAPPING[filter_value])  # noqa: WPS529

        if filter_value == 'active':
            queryset = queryset.filter(
                status=SurveyStatus.ACTIVE,
                end_date__isnull=False,
                end_date__gte=now_date,
            )

        if filter_value == 'finished':
            queryset = queryset.filter(
                models.Q(status=SurveyStatus.COMPLETED)
                | models.Q(end_date__isnull=False, end_date__lt=now_date)
            )

        return queryset
