from typing import NotRequired, TypedDict

import pytest
from polyfactory.factories import TypedDictFactory
from polyfactory.pytest_plugin import register_fixture


class TGChat(TypedDict):
    """Represents a Telegram chat object."""

    id: int
    first_name: str
    last_name: str
    username: str
    type: NotRequired[str]


class TGUser(TypedDict):
    """Represents a Telegram user object."""

    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str
    language_code: NotRequired[str]


class TGMessage(TypedDict):
    """Represents a Telegram message object."""

    message_id: int
    from_user: TGUser
    chat: TGChat
    date: int
    text: str


class TGUpdate(TypedDict):
    """Represents a Telegram update object."""

    update_id: int
    message: TGMessage


class TGApiAnswer(TypedDict):
    """Represents a standard Telegram API response structure."""

    result: TGUpdate  # noqa: WPS110
    ok: NotRequired[bool]


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
