from typing import final
from unittest.mock import MagicMock, Mock

import pytest
from polyfactory.factories import TypedDictFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from pydantic import BaseModel, Field
from pytest_mock import MockerFixture
from telebot import TeleBot

from tests.plugins.tgbot.api_factory import TGApiAnswer


@register_fixture(name='tg_api_answer_factory')
class TGApiAnswerFactory(TypedDictFactory[TGApiAnswer]):
    """Factory for generating mock Telegram API response."""

    __check_model__ = False
    ok = True


@pytest.fixture
def tg_api_answer(
    tg_api_answer_factory: TGApiAnswerFactory,
) -> TGApiAnswer:
    """Returns tg_api_answer_factory fixture build result."""
    return tg_api_answer_factory.build()


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


class _Chat(BaseModel):
    id: int
    type: str = 'private'


class MockMessage(BaseModel):
    """Message test DTO."""

    message_id: int = Field(gt=0)
    from_user: _User | None
    chat: _Chat
    text: str | None = None


@pytest.fixture
def mock_bot_send_message(mocker: MockerFixture) -> MagicMock:
    """Mock the `telebot.TeleBot.send_message` method."""
    return mocker.patch('telebot.TeleBot.send_message')


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


@pytest.fixture
def message_with_user(
    tg_message_factory: MessageFactory,
    tg_message_user_factory: _UserFactory,
) -> MockMessage:
    """Get ok message."""
    return tg_message_factory.build(from_user=tg_message_user_factory.build())
