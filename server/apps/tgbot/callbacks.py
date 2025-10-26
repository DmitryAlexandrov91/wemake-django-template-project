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


answer_callback = CallbackFactory(
    'answer_id', 'survey_result_id', prefix='edit', config={}
)
answer_cancel_callback = CallbackFactory(
    'answer_id', 'survey_result_id', prefix='cancel', config={}
)
