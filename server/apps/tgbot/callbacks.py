from typing import Any

from telebot import callback_data


class CallbackFactory:
    """Factory for create callback objects."""

    def __init__(
        self, *parts: str, prefix: str, config: dict[str, Any]
    ) -> None:
        """Create CallbackData and CallbackDataFilter instances."""
        self.factory = callback_data.CallbackData(*parts, prefix=prefix)

        self.filter = callback_data.CallbackDataFilter(
            factory=self.factory, config=config
        )


SURVEY_RESULT_ID = 'survey_result_id'


survey_list_callback = CallbackFactory(
    'survey_id', 'user_id', prefix='surveys', config={}
)
back_to_active_surveys = CallbackFactory(
    SURVEY_RESULT_ID, prefix='back_to_surveys', config={}
)
answer_callback = CallbackFactory(
    'answer_id', SURVEY_RESULT_ID, prefix='edit', config={}
)
answer_cancel_callback = CallbackFactory(
    'answer_id', SURVEY_RESULT_ID, prefix='cancel', config={}
)
survey_callback = CallbackFactory(
    SURVEY_RESULT_ID,
    'question_id',
    'answer_option',
    prefix='survey',
    config={},
)
