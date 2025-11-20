from datetime import timedelta

from django.utils import timezone

from server.apps.surveys.choices import SurveyStatus
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
    is_favorite = False
    status = SurveyStatus.DRAFT
    five_days_shift = timedelta(days=5)
    one_day_shift = timedelta(days=1)
    ten_days_shift = timedelta(days=10)
    if filter_param == 'favorite':
        start_date = today - one_day_shift
        end_date = today + five_days_shift
        is_favorite = True
    elif filter_param == 'finished':
        start_date = today - ten_days_shift
        end_date = today - one_day_shift
        status = SurveyStatus.COMPLETED
    elif filter_param == 'archive':
        start_date = today - ten_days_shift
        end_date = today + one_day_shift
        status = SurveyStatus.ARCHIVED
    elif filter_param == 'active':
        start_date = today - ten_days_shift
        end_date = today + five_days_shift
        status = SurveyStatus.ACTIVE
    else:
        start_date = today
        end_date = today + five_days_shift
    return surveys_survey_factory(
        department=department_factory(),
        title=filter_param,
        start_date=start_date,
        end_date=end_date,
        is_favorite=is_favorite,
        status=status,
    )
