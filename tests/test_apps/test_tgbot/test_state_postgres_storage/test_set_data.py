import pytest

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_set_data(
    message_with_user: MockMessage,
) -> None:
    """Test ensure that set_data method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    assert len(TgUserState.objects.all()) == 0

    state_key, state_value = 'text', 'Hello!'

    resolve(StatePostgresStorage).set_data(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        key=state_key,
        value=state_value,
    )

    state_obj = TgUserState.objects.get(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )

    assert state_obj.state_data[state_key] == state_value
