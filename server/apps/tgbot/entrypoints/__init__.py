from server.apps.tgbot.entrypoints import edit as edit
from server.apps.tgbot.entrypoints import start as start
from server.apps.tgbot.entrypoints import survey as survey
from server.apps.tgbot.entrypoints.edit import (  # noqa: F401
    handle_cancel_edit_answer,
    handle_edit_answer,
    handle_new_answer_text,
    responses_edit_handler,
)
from server.apps.tgbot.entrypoints.menu import (  # noqa: F401
    handle_archive_answers_for_period,
    handle_show_archive_answers,
    handle_start_date,
    menu_handler,
)
from server.apps.tgbot.entrypoints.start import start_handler  # noqa: F401
