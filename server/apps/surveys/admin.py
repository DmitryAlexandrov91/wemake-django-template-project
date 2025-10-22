from typing import override

from django.contrib import admin
from django.db.models import Prefetch, QuerySet
from django.forms.models import ModelForm
from django.http import HttpRequest

from server.apps.surveys.admin_common import QuestionInline
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    StatisticSettings,
    Suggestion,
    Survey,
    SurveyResult,
    UserAnswer,
)
from server.apps.surveys.tasks import update_user_statistics_task


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin[Survey]):
    """Admin class for surveys."""

    list_display = (
        'id',  # noqa: WPS226
        'title',  # noqa: WPS226
        'start_date',
        'end_date',
    )
    search_fields = ('title', 'id')
    ordering = ('-start_date',)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin[Question]):
    """Admin class for questions."""

    list_display = (
        'id',
        'text',  # noqa: WPS226
        'question_type',
        'get_surveys',  # noqa: WPS226
    )
    list_filter = ('question_type', 'surveys')
    search_fields = ('text',)

    @admin.display(description='Surveys')
    def get_surveys(self, question: Question) -> str:
        """Get surveys."""
        return ', '.join(survey.title for survey in question.surveys.all())

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        """Get queryset with prefetch."""
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch('surveys', queryset=Survey.objects.only('title'))
            )
        )


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin[AnswerOption]):
    """Admin class for answer options."""

    list_display = (
        'id',
        'text',
        'question',  # noqa: WPS226
    )
    list_select_related = ('question',)
    search_fields = ('text', 'question__text')


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin[SurveyResult]):
    """Admin class for survey result."""

    list_display = (
        'id',
        'user',  # noqa: WPS226
        'survey',
    )
    list_filter = ('survey',)
    search_fields = (
        'user__username',
        'user__email',
        'survey__title',
    )
    list_select_related = ('user', 'survey')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin[UserAnswer]):
    """Admin class for user answer."""

    list_display = (
        'survey_result',
        'question',
    )
    list_select_related = (
        'survey_result__user',
        'survey_result__survey',
        'question',
    )


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin[Suggestion]):
    """Admin class for suggestions."""

    list_display = (
        'id',
        'user',  # noqa: WPS226
        'title',  # noqa: WPS226
        'description',
    )
    search_fields = (
        'user__username',
        'title',  # noqa: WPS226
        'description',
    )
    list_select_related = ('user',)


@admin.register(StatisticSettings)
class StatisticSettingsAdmin(admin.ModelAdmin[StatisticSettings]):
    """Admin class for statistic settings."""

    list_display = ('survey_response_avg_period',)

    @override
    def save_model(
        self,
        request: HttpRequest,
        settings_obj: StatisticSettings,
        form: ModelForm[StatisticSettings],
        change: bool,
    ) -> None:
        """Save new statistic settings starts update user statistics."""
        super().save_model(request, settings_obj, form, change)
        if (
            change
            and form.has_changed()
            and 'survey_response_avg_period' in form.changed_data
        ):
            update_user_statistics_task.delay()
