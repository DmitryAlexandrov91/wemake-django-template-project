from typing import Literal, TypedDict

from django.conf import settings
from rest_framework.response import Response


class CookieConfig(TypedDict, total=False):
    """Access cookie configuration."""

    key: str
    value: str  # noqa: WPS110
    max_age: int
    httponly: bool
    secure: bool
    samesite: Literal['Lax', 'Strict', 'None', False]
    path: str


def build_cookie_config(
    key: str,
    cookie_value: str,
    max_age: int,
    path: str,
) -> CookieConfig:
    """Build Cookie config."""
    config: CookieConfig = {
        'key': key,
        'value': cookie_value,
        'max_age': max_age,
        'path': path,
        'httponly': True,
        'secure': True,
        'samesite': settings.JWT_COOKIE['SAMESITE'],
    }
    return config


def set_cookie(response: Response, config: CookieConfig) -> Response:
    """
    Set a cookie with the given name, value, and attributes.

    Args:
        response (Response): DRF response object.
        config (CookieConfig): TypeDict for cookie attrs.
    """
    response.set_cookie(**config)
    return response


def clear_cookie(
    response: Response, cookie_name: str, path: str = '/'
) -> Response:
    """
    Clear a cookie by setting its value to empty and max_age to 0.

    Args:
        response (Response): DRF response object.
        cookie_name (str): Cookie name.
        path (str): Path for which the cookie is valid.
    """
    response.set_cookie(
        key=cookie_name,
        value='',
        max_age=0,
        httponly=settings.JWT_COOKIE['HTTPONLY'],
        secure=settings.JWT_COOKIE['SECURE'],
        samesite=settings.JWT_COOKIE['SAMESITE'],
        path=path,
    )
    return response
