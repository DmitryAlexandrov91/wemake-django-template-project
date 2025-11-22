from dataclasses import dataclass

from telebot.types import InlineKeyboardButton

from server.apps.tgbot.callbacks import back_to_active_surveys
from server.apps.tgbot.message_templates import BACK_TO_SURVEYS
from server.apps.tgbot.services.keyboard_builder import ButtonBuilderService


@dataclass
class BackToSurveysButton:
    """Button for rerurn to user active serveys list."""

    _button_builder: ButtonBuilderService

    def __call__(self, survey_result_id: int) -> InlineKeyboardButton:
        """Return button for back to active surveys list."""
        return self._button_builder(
            text=BACK_TO_SURVEYS,
            callback=back_to_active_surveys,
            callback_data={'survey_result_id': survey_result_id},
        )
