from django.contrib import admin

from server.apps.surveys.models import (
    Survey,
    SurveyQuestion,
)


class QuestionInline(admin.TabularInline[SurveyQuestion, Survey]):
    """Question in Surveys."""

    model = SurveyQuestion
    extra = 1
