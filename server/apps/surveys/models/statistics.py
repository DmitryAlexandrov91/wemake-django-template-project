from typing import override

from django.conf import settings
from django.db import models


class StatisticSettings(models.Model):
    """Settings to tune the statistics."""

    survey_response_avg_period = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_USER_STAT_PERIOD,
        help_text=(
            'How many latest surveys are taken into account while calculating'
            ' the question response average time for the user.'
        ),
    )
    singleton = models.BooleanField(default=True, editable=False)

    class Meta:
        verbose_name = 'statistics settings'
        verbose_name_plural = 'statistics settings'
        constraints = (
            models.UniqueConstraint(
                fields=['singleton'], name='single_instance_constraint'
            ),
        )
        default_related_name = 'stat_settings'

    @override
    def __str__(self) -> str:
        """
        Str method for statistic settings.

        >>> instance = StatisticSettings()
        >>> str(instance)
        'Statistic settings'
        """
        return 'Statistic settings'


class UserStatistics(models.Model):
    """User statistic data."""

    user = models.OneToOneField(
        to='users.CustomUser',
        on_delete=models.CASCADE,
    )
    average_answer_sec = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'user statistics'
        verbose_name_plural = 'user statistics'
        default_related_name = 'statistics'
