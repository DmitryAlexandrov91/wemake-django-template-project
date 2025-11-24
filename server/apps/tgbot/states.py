import enum


class EditState(enum.StrEnum):
    """State for edit answer."""

    waiting_for_new_answer = 'EditState:waiting_for_new_answer'


class SurveyResponseState(enum.StrEnum):
    """State for handle survey answer response."""

    survey_response = 'SurveyResponseState:survey_response'


class SurveyPeriodStates(enum.StrEnum):
    """States for handling the survey results period input from the user."""

    waiting_for_start_date = 'waiting_for_start_date'
    waiting_for_end_date = 'waiting_for_end_date'


class SuggestState(enum.StrEnum):
    """States for receiving user suggestions."""

    waiting_for_suggestion = 'SuggestState:waiting_for_suggestion'
