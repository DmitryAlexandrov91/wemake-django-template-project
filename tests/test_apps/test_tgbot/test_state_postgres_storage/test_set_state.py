import pytest

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_set_state(message_with_user: MockMessage) -> None:
    """Test ensure that set_state method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    state_for_install = 'test_state'

    resolve(StatePostgresStorage).set_state(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        state=str(state_for_install),
    )

    state_obj = TgUserState.objects.get(state=state_for_install)

    assert state_obj.state == str(state_for_install)
