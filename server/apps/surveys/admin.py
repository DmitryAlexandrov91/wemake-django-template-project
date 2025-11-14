# flake8: noqa: WPS226
from typing import Any, override

from django.contrib import admin
from django.db.models import Prefetch, QuerySet
from django.db.models.fields.related import ForeignKey
from django.forms import ModelChoiceField, models
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
from server.apps.surveys.tasks.tasks import update_user_statistics_task


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin[Survey]):
    """Admin class for surveys."""

    list_display = (
        'id',
        'title',
        'status',
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
        'text',
        'question_type',
        'get_surveys',
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
        'question',
    )
    list_select_related = ('question',)
    search_fields = ('text', 'question__text')


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin[SurveyResult]):
    """Admin class for survey result."""

    list_display = (
        'id',
        'user',
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
    """Admin interface for UserAnswer model."""

    list_display = ('survey_result', 'question')
    list_select_related = (
        'survey_result__user',
        'survey_result__survey',
        'question',
    )
    fields = (
        'survey_result',
        'question',
        'text_answer',
        'selected_options',
    )
    list_filter = ('survey_result__user', 'survey_result__survey', 'question')
    search_fields = ('text_answer',)

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[UserAnswer]:
        """Advanced queryset."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'survey_result',
            'survey_result__survey',
            'survey_result__user',
            'question',
        ).prefetch_related('selected_options')

    @override
    def formfield_for_foreignkey(
        self,
        db_field: ForeignKey[Any],
        request: HttpRequest,
        **kwargs: Any,
    ) -> ModelChoiceField[Any] | None:
        if db_field.name == 'survey_result':
            kwargs['queryset'] = SurveyResult.objects.select_related('user')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin[Suggestion]):
    """Admin class for suggestions."""

    list_display = (
        'id',
        'user',
        'title',
        'description',
    )
    search_fields = (
        'user__username',
        'title',
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
        form: models.ModelForm[StatisticSettings],
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
