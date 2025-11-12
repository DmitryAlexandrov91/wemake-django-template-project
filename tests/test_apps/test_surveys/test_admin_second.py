from typing import TYPE_CHECKING, Any, cast

import pytest
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest

from server.apps.surveys.admin import UserAnswerAdmin
from server.apps.surveys.models import (
    Question,
    SurveyResult,
    UserAnswer,
)

if TYPE_CHECKING:
    SurveyResultFK = ForeignKey[SurveyResult, Any]
else:
    SurveyResultFK = ForeignKey


@pytest.mark.django_db
def test_formfield_for_foreignkey(
    user_answer_admin_instance: UserAnswerAdmin,
    user_answer_complex: UserAnswer,
) -> None:
    """Test formfield_for_foreignkey."""
    survey_result_fk = UserAnswer._meta.get_field('survey_result')  # noqa: SLF001
    typed_fk = cast(SurveyResultFK, survey_result_fk)
    kwargs: dict[str, Any] = {}
    field = user_answer_admin_instance.formfield_for_foreignkey(
        typed_fk, HttpRequest(), **kwargs
    )
    assert isinstance(field, ModelChoiceField)
    assert field.queryset is not None
    assert field.queryset.model is SurveyResult

    select_related = field.queryset.query.select_related
    assert isinstance(select_related, dict)
    assert 'user' in select_related


@pytest.mark.django_db
def test_formfield_for_foreignkey_no_surveyres(
    user_answer_admin_instance: UserAnswerAdmin,
) -> None:
    """Test if condition is not met in formfield_for_foreignkey."""
    question_fk = UserAnswer._meta.get_field('question')  # noqa: SLF001
    typed_fk = cast(ForeignKey[Question, Any], question_fk)
    kwargs: dict[str, Any] = {}
    field = user_answer_admin_instance.formfield_for_foreignkey(
        typed_fk, HttpRequest(), **kwargs
    )
    assert isinstance(field, ModelChoiceField)
    assert field.queryset is not None
    assert field.queryset.model is Question
    assert field.queryset.query.select_related is False
