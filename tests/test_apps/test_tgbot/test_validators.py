import pytest

from server.apps.tgbot.usecases.validators import recognize_survey_id
from server.common.layouts import SURVEY_KEY

START_PREFIX = '/start '


@pytest.mark.parametrize(
    ('input_text', 'expected_id'),
    [
        (f'{START_PREFIX}{SURVEY_KEY}0', 0),
        (f'{START_PREFIX}{SURVEY_KEY}1', 1),
        (f'{START_PREFIX}{SURVEY_KEY}10', 10),
        (f'{START_PREFIX}{SURVEY_KEY}999abrakadabra', 999),
        ('Text without numbers', None),
    ],
)
def test_recognize_survey_id_found(input_text: str, expected_id: int) -> None:
    """Test survey key recognized."""
    assert recognize_survey_id(input_text) == expected_id
