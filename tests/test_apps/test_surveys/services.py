from datetime import timedelta

from django.utils import timezone

from server.apps.surveys.models import Survey
from tests.plugins.department_factory import DepartmentFactory
from tests.plugins.surveys_survey import SurveyFactory

END_DATE_ATTR = 'end_date'
START_DATE_ATTR = 'start_date'


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
