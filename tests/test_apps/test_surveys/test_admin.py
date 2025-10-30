from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.forms import ModelForm
from django.http import HttpRequest

from server.apps.surveys.admin import QuestionAdmin
from server.apps.surveys.models import Question, Survey
from tests.plugins.surveys_admin import AdminSetup

SURVEY_RESP_ATTR = 'survey_response_avg_period'


@pytest.mark.django_db
def test_get_surveys(  # noqa: WPS234
    question_admin: QuestionAdmin,
    question_with_two_surveys: Callable[
        [dict[str, Any]], tuple[Question, list[Survey]]
    ],
) -> None:
    """Test get_surveys."""
    question, surveys = question_with_two_surveys({
        'text': 'test text',
        'question_type': 'score',
    })
    result_data: str = question_admin.get_surveys(question)
    expected: str = ', '.join(survey.title for survey in surveys)
    assert result_data == expected


@pytest.mark.django_db
def test_get_surveys_empty(
    question_admin: QuestionAdmin,
    surveys_question_factory: Callable[..., Question],
) -> None:
    """Test empty."""
    question: Question = surveys_question_factory(text='Empty question?')
    assert not question_admin.get_surveys(question)


@pytest.mark.django_db
def test_get_queryset_prefetch(  # noqa: WPS234
    admin_user: Any,
    rf: Any,
    question_with_two_surveys: Callable[
        [dict[str, Any]], tuple[Question, list[Survey]]
    ],
    question_admin: QuestionAdmin,
) -> None:
    """Test prefetch."""
    question, _ = question_with_two_surveys({})
    request: HttpRequest = rf.get('/admin/app/question/')
    request.user = admin_user
    queryset = question_admin.get_queryset(request)
    assert hasattr(queryset, 'prefetch_related')
    assert question in list(queryset)


def test_save_model_without_changes(
    save_stat_settings_setup: AdminSetup,
) -> None:
    """Test save method when no changes are made in the form."""
    settings_obj = save_stat_settings_setup['settings_obj']
    request = save_stat_settings_setup['factory'].post('/admin/url/')
    request.user = save_stat_settings_setup['user']
    form = MagicMock()
    form.has_changed.return_value = False
    form.changed_data = []
    save_stat_settings_setup['admin'].save_model(
        request, settings_obj, form, change=True
    )
    assert form.has_changed() is False


def test_save_model_with_period_change(
    save_stat_settings_setup: AdminSetup,
) -> None:
    """Test custom save method in statistics admin."""
    settings_obj = save_stat_settings_setup['settings_obj']
    request = save_stat_settings_setup['factory'].post('/admin/url/')
    request.user = save_stat_settings_setup['user']
    admin = save_stat_settings_setup['admin']

    form = MagicMock(spec=ModelForm)
    form.has_changed.return_value = True
    form.changed_data = [SURVEY_RESP_ATTR]
    form.cleaned_data = {SURVEY_RESP_ATTR: 14}
    settings_obj.survey_response_avg_period = 14

    admin.save_model(request, settings_obj, form, change=True)

    settings_obj.refresh_from_db()
    assert settings_obj.survey_response_avg_period == 14
