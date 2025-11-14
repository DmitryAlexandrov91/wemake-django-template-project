# flake8: noqa: WPS412
from server.apps.surveys.tasks.status import (
    turn_one_survey_status_task as turn_one_survey_status_task,
)
from server.apps.surveys.tasks.status import (
    turn_survey_active_to_complet_task as turn_survey_active_to_complet_task,
)
from server.apps.surveys.tasks.tasks import (
    delete_marked_questions_task as delete_marked_questions_task,
)
from server.apps.surveys.tasks.tasks import (
    delete_marked_surveys_task as delete_marked_surveys_task,
)
from server.apps.surveys.tasks.tasks import (
    delete_one_question_task as delete_one_question_task,
)
from server.apps.surveys.tasks.tasks import (
    delete_one_survey_task as delete_one_survey_task,
)
from server.apps.surveys.tasks.tasks import (
    email_survey_invitation_task as email_survey_invitation_task,
)
from server.apps.surveys.tasks.tasks import (
    update_one_user_statistics_task as update_one_user_statistics_task,
)
from server.apps.surveys.tasks.tasks import (
    update_user_statistics_task as update_user_statistics_task,
)

__all__ = [
    'delete_marked_questions_task',
    'delete_marked_surveys_task',
    'delete_one_question_task',
    'delete_one_survey_task',
    'email_survey_invitation_task',
    'turn_one_survey_status_task',
    'turn_survey_active_to_complet_task',
    'update_one_user_statistics_task',
    'update_user_statistics_task',
]
