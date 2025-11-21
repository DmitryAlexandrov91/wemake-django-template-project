import pytest

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_get_data(
    message_with_user: MockMessage,
    fakery_m: FakeryM[TgUserState],
) -> None:
    """Test ensure that get_data method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    get_data_method = resolve(StatePostgresStorage).get_data

    empty_data = get_data_method(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )
    assert empty_data == {}

    test_state_data = {'text': 'Hello boss'}
    state_obj = fakery_m(TgUserState)(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        state_data=test_state_data,
    )

    assert (
        get_data_method(
            chat_id=message_with_user.chat.id,
            user_id=message_with_user.from_user.id,
        )
        == state_obj.state_data
    )
