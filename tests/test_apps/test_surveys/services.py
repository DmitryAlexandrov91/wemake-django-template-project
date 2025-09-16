from datetime import timedelta
from typing import Any

from django.utils import timezone

from server.apps.surveys.models import Survey
from tests.plugins.department_factory import DepartmentFactory
from tests.plugins.surveys_survey import SurveyFactory

END_DATE_ATTR = 'end_date'
START_DATE_ATTR = 'start_date'
TEXT_ATTR = 'text'
IS_CORRECT_ATTR = 'is_correct'


def build_survey(  # noqa: WPS210
    filter_param: str,
    department_factory: DepartmentFactory,
    surveys_survey_factory: SurveyFactory,
) -> Survey:
    """Build survey`s instance by filter param."""
    today = timezone.now().date()
    start_date = today
    end_date = today + timedelta(days=5)
    is_favorite = False
    five_days_shift = timedelta(days=5)
    one_daye_shift = timedelta(days=1)
    ten_days_shift = timedelta(days=10)
    if filter_param == 'favorite':
        start_date = today - one_daye_shift
        end_date = today + five_days_shift
        is_favorite = True
    elif filter_param == 'drafts':
        start_date = today + one_daye_shift
        end_date = today + five_days_shift
    elif filter_param == 'finished':
        start_date = today - ten_days_shift
        end_date = today
    else:
        start_date = today - ten_days_shift
        end_date = today - five_days_shift
    return surveys_survey_factory(
        department=department_factory(),
        title=filter_param,
        start_date=start_date,
        end_date=end_date,
        is_favorite=is_favorite,
    )


def get_survey_json(answers_count: int | None = 2) -> dict[str, Any]:
    """Build survey json."""
    json_data: dict[str, Any] = {
        'name': 'Customer feedback',
        'comment': 'Short survey',
        'started_at': '2025-09-15',
        'finished_at': '2025-09-25',
        'is_favorite': False,
        'department': {'department_name': 'HR'},
    }
    questions: list[dict[str, Any]] = []
    json_data['questions'] = questions
    for question_index in range(3):
        answers: list[dict[str, Any]] = []
        if answers_count:
            for answer_index in range(answers_count):
                list.append(
                    answers,
                    {TEXT_ATTR: f'{answer_index}', IS_CORRECT_ATTR: True},
                )
        json_data['questions'].append({
            TEXT_ATTR: f'question_{question_index}',
            'type': 'score',
            'is_favorite': False,
            'answers': answers,
        })
    return json_data
