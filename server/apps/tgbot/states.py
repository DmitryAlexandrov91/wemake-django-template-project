from telebot.handler_backends import (  # type: ignore[attr-defined]
    State,
    StatesGroup,
)


class EditStates(StatesGroup):
    """State for edit answer."""

    waiting_for_new_answer = State()
