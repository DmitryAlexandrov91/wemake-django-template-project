import re

from server.common.layouts import SURVEY_KEY


def recognize_survey_id(txt: str) -> int | None:
    """Cut the survey id if submitted."""
    match = re.search(f'{re.escape(SURVEY_KEY)}(\\d+)', txt)
    if not match:
        return None
    return int(match.group(1))
