import pytest

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_reset_data(
    message_with_user: MockMessage,
    fakery_m: FakeryM[TgUserState],
) -> None:
    """Test ensure that reset_data method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    test_data = {'text': 'good'}

    state_obj_with_data = fakery_m(TgUserState)(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        state_data=test_data,
    )
    assert state_obj_with_data.state_data == test_data

    resolve(StatePostgresStorage).reset_data(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )
    state_obj_with_data.refresh_from_db()

    assert state_obj_with_data.state_data == {}
