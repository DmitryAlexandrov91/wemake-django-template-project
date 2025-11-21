import pytest

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_delete_state(
    message_with_user: MockMessage,
    fakery_m: FakeryM[TgUserState],
) -> None:
    """Test ensure that delete_state method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    test_state = 'test_delete_state'

    state_obj_with_state = fakery_m(TgUserState)(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        state=test_state,
    )

    assert state_obj_with_state.state == test_state

    resolve(StatePostgresStorage).delete_state(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )

    with pytest.raises(TgUserState.DoesNotExist):
        TgUserState.objects.get(
            chat_id=message_with_user.chat.id,
            user_id=message_with_user.from_user.id,
        )
