import pytest

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_get_state(
    message_with_user: MockMessage,
    fakery_m: FakeryM[TgUserState],
) -> None:
    """Test ensure that get_state method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    state = resolve(StatePostgresStorage).get_state(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )
    assert state is None

    state_obj_with_state = fakery_m(TgUserState)(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        state='test_state',
    )

    state = resolve(StatePostgresStorage).get_state(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )

    assert state == state_obj_with_state.state == 'test_state'
