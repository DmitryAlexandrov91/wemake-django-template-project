from typing import NotRequired, TypedDict


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
