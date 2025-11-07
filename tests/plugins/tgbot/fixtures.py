from typing import final
from unittest.mock import MagicMock, Mock

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from pydantic import BaseModel, Field
from pytest_mock import MockerFixture
from telebot import TeleBot

from server.apps.users.models import CustomUser


@pytest.fixture
def mock_bot() -> Mock:
    """Returns mock tg bot."""
    return Mock(TeleBot)


class _User(BaseModel):
    id: int = Field(gt=0)
    is_bot: bool = False
    first_name: str
    last_name: str | None = None
    username: str
    tg_username: str | None = None


class _Chat(BaseModel):
    id: int
    type: str = 'private'


class MockMessage(BaseModel):
    """Message test DTO."""

    id: int = Field(gt=0)
    message_id: int = Field(gt=0)
    from_user: _User | None
    chat: _Chat
    text: str | None
    date: int


class TGUpdate(BaseModel):
    """Update test DTO."""

    update_id: int
    message: MockMessage


class TGApiAnswer(BaseModel):
    """TG Api answer test DTO."""

    result: TGUpdate  # noqa: WPS110
    ok: bool = True


class MockCallbackQuery(BaseModel):
    """CallbackQuery test DTO."""

    id: str = Field(min_length=1)
    from_user: _User
    message: MockMessage
    chat_instance: str = Field(min_length=1)
    data: str | None = None  # noqa: WPS110
    inline_message_id: str


class MockUpdateWithCallbackQuery(BaseModel):
    """Update with CallbackQuery test DTO."""

    update_id: int
    callback_query: MockCallbackQuery


class TGApiCallbackAnswer(BaseModel):
    """TG Api callback answer test DTO."""

    result: MockUpdateWithCallbackQuery  # noqa: WPS110
    ok: bool = True


@pytest.fixture
def mock_bot_send_message(mocker: MockerFixture) -> MagicMock:
    """Mock the `telebot.TeleBot.send_message` method."""
    return mocker.patch('telebot.TeleBot.send_message')


@pytest.fixture
def mock_bot_edit_message_text(mocker: MockerFixture) -> MagicMock:
    """Mock the `telebot.TeleBot.edit_message_text` method."""
    return mocker.patch('telebot.TeleBot.edit_message_text')


@pytest.fixture
def mock_bot_delete_message(mocker: MockerFixture) -> MagicMock:
    """Mock the `telebot.TeleBot.delete_message` method."""
    return mocker.patch('telebot.TeleBot.delete_message')


@pytest.fixture
def mock_bot_answer_callback_query(mocker: MockerFixture) -> MagicMock:
    """Mock the `telebot.TeleBot.answer_callback_query` method."""
    return mocker.patch('telebot.TeleBot.answer_callback_query')


@final
@register_fixture(name='tg_message_factory')
class MessageFactory(ModelFactory[MockMessage]):
    """Factory to create custom tg messages."""

    __set_as_default_factory_for_type__ = True
    __check_model__ = False


@final
@register_fixture(name='tg_message_user_factory')
class _UserFactory(ModelFactory[_User]):
    """Factory to create full user."""

    __set_as_default_factory_for_type__ = True
    __check_model__ = False
    __allow_none_optionals__ = False


@final
@register_fixture(name='tg_callback_query_factory')
class CallbackQueryFactory(ModelFactory[MockCallbackQuery]):
    """Factory to create custom tg callback queries."""

    __set_as_default_factory_for_type__ = True
    __check_model__ = False


@pytest.fixture
def message_with_user(
    tg_message_factory: MessageFactory,
    tg_message_user_factory: _UserFactory,
) -> MockMessage:
    """Get ok message."""
    return tg_message_factory.build(from_user=tg_message_user_factory.build())


@register_fixture(name='tg_api_answer_factory')
class TGApiAnswerFactory(ModelFactory[TGApiAnswer]):
    """Get mock Telegram API response."""

    __check_model__ = False


@pytest.fixture
def tg_api_answer(
    tg_api_answer_factory: TGApiAnswerFactory,
) -> TGApiAnswer:
    """
    Returns tg_api_answer_factory fixture build result.

    If you need dict obj, use model_dump() method.
    """
    return tg_api_answer_factory.build()


@pytest.fixture
def mock_callback_query(
    tg_callback_query_factory: CallbackQueryFactory,
    tg_message_user_factory: _UserFactory,
    message_with_user: MockMessage,
) -> MockCallbackQuery:
    """Get mock callback query with message and user."""
    return tg_callback_query_factory.build(
        from_user=tg_message_user_factory.build(),
        message=message_with_user,
    )


@pytest.fixture
def mock_start_message_with_auth_user(
    auth_user: CustomUser,
) -> Mock:
    """Mocks the start tg message with given user and survey."""
    message = Mock()
    message.chat = Mock(id=12345)
    message.text = '/start'
    message.from_user = Mock(
        id=auth_user.id,
        username=auth_user.tg_username[1:],
        first_name=auth_user.full_name,
    )
    return message
