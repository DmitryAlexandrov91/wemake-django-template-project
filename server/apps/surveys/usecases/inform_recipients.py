import os

import telebot

from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import Survey
from server.apps.surveys.tasks import email_survey_invitation_task
from server.common.layouts import (
    END_DATE_LAYOUT,
    LINK_LAYOUT,
    MESSAGE_LAYOUT,
    SUBJECT_LAYOUT,
    SURVEY_KEY,
)
from server.di import resolve
from server.settings.components import common

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN', 'tg_bot_false_token')


def get_bot_username() -> str | None:
    """Get the username of the tg-bot."""
    return telebot.TeleBot(TG_BOT_TOKEN).get_me().username


def survey_notification(survey: Survey) -> None:
    """Sending survey invitation emails after survey creation."""
    tg_bot_username = get_bot_username()
    if not tg_bot_username:
        raise ValueError('No bot username received.')

    end_date_add = (
        END_DATE_LAYOUT.format(survey.end_date.strftime('%d.%m.%Y'))
        if survey.end_date
        else ''
    )
    for user in resolve(SurveyRepo).get_survey_recipients(survey=survey):
        message = MESSAGE_LAYOUT.format(
            user.full_name,
            survey.title,
            survey.start_date.strftime('%d.%m.%Y'),
            end_date_add,
            LINK_LAYOUT.format(tg_bot_username, SURVEY_KEY, survey.id),
        )
        email_survey_invitation_task.delay(
            subject=SUBJECT_LAYOUT.format(survey.title),
            message=message,
            from_email=common.DEFAULT_FROM_EMAIL,
            to_emails=[user.email],
        )
