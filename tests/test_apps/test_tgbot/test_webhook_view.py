from http import HTTPStatus
from typing import Any

import pytest
from django.conf import LazySettings
from django.test import Client

from server.di import resolve
from tests.plugins.tgbot.fixtures import TGApiAnswer

CONTENT_TYPE = 'application/json'
settings = resolve(LazySettings)


@pytest.fixture(name='header_with_current_secret')
def current_header() -> dict[Any, Any]:
    """Return header with curren webhook secret."""
    return {
        'X-Telegram-Bot-API-Secret-Token': settings.WEBHOOK_SECRET,
    }


@pytest.mark.parametrize(
    'method',
    ['get', 'put', 'patch', 'delete', 'options', 'head'],
)
def test_webhook_endpoint_not_allowed_methods(
    client: Client, method: str
) -> None:
    """Test that webhook endpoint rejects non-POST methods."""
    http_method = getattr(client, method)
    response = http_method(settings.WEBHOOK_PATH)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_webhook_invalid_secret_token(
    client: Client,
    tg_api_answer: TGApiAnswer,
) -> None:
    """Test invalid secret token."""
    response = client.post(settings.WEBHOOK_PATH)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.content == b'Invalid secret token'

    headers = {
        'X-Telegram-Bot-API-Secret-Token': 'invalid_secret',
    }

    response = client.post(
        path=settings.WEBHOOK_PATH,
        data=tg_api_answer.model_dump(mode='json')['result'],  # noqa: WPS226
        headers=headers,
        content_type=CONTENT_TYPE,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.content == b'Invalid secret token'


def test_webhook_valid_update(
    client: Client,
    header_with_current_secret: dict[Any, Any],
    tg_api_answer: TGApiAnswer,
) -> None:
    """Test webhook with current headers and update from tg."""
    response = client.post(
        settings.WEBHOOK_PATH,
        headers=header_with_current_secret,
        content_type=CONTENT_TYPE,
        data=tg_api_answer.model_dump(mode='json')['result'],
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content == b'ok'


def test_custom_webhook_path(
    client: Client,
    header_with_current_secret: dict[Any, Any],
    tg_api_answer: TGApiAnswer,
) -> None:
    """Custom webhook path test."""
    response = client.post(
        settings.WEBHOOK_PATH,
        headers=header_with_current_secret,
        content_type=CONTENT_TYPE,
        data=tg_api_answer.model_dump(mode='json')['result'],
    )

    assert response.status_code == HTTPStatus.OK
