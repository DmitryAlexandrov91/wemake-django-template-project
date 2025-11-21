import pytest
from telebot.storage import StateDataContext

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.models import TgUserState
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_storage_get_intaractive_data(
    message_with_user: MockMessage,
    fakery_m: FakeryM[TgUserState],
) -> None:
    """Test ensure that get_intaractive_data method works correctly."""
    assert message_with_user.from_user is not None
    assert message_with_user.from_user.id is not None

    test_state_data = {'text': 'Hello boss'}
    state_obj_with_data = fakery_m(TgUserState)(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
        state_data=test_state_data,
    )

    context = resolve(StatePostgresStorage).get_interactive_data(
        chat_id=message_with_user.chat.id,
        user_id=message_with_user.from_user.id,
    )
    assert isinstance(context, StateDataContext)

    new_data_for_update = 'New data for state update'
    with context as state_data:
        assert state_data == state_obj_with_data.state_data
        state_data['new_data'] = new_data_for_update

    state_obj_with_data.refresh_from_db()
    assert 'new_data' in state_obj_with_data.state_data
