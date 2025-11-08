from telebot.handler_backends import (  # type: ignore[attr-defined]
    State,
    StatesGroup,
)


class EditStates(StatesGroup):
    """State for edit answer."""

    waiting_for_new_answer = State()


class SurveyPeriodStates(StatesGroup):
    """States for handling the survey results period input from the user."""

    waiting_for_start_date = State()
    waiting_for_end_date = State()
