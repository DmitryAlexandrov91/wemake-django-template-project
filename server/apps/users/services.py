from typing import Any

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from server.apps.users.cookies_utils import (
    CookieConfig,
    build_cookie_config,
    clear_cookie,
    set_cookie,
)


class AuthService:
    """Class for user`s authentication methods."""

    def authenticate_user(
        self,
        serializer: serializers.BaseSerializer[Any],
    ) -> Response:
        """Auth user."""
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            detail = getattr(exc, settings.EXCEPTION_DETAIL_ATRR, None)
            if detail and getattr(detail, 'code', '') == 'no_active_account':
                return Response(
                    {settings.EXCEPTION_DETAIL_ATRR: 'Invalid credentials.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {settings.EXCEPTION_DETAIL_ATRR: str(detail or exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh: RefreshToken = RefreshToken.for_user(serializer.user)  # type: ignore[attr-defined]
        response = Response(
            serializer.validated_data, status=status.HTTP_200_OK
        )
        return self.attach_jwt_cookies(response, refresh=refresh)

    def refresh_access_token(
        self,
        serializer: serializers.BaseSerializer[Any],
    ) -> Response:
        """Update access and refresh token for auth user."""
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError):
            return Response(
                {settings.EXCEPTION_DETAIL_ATRR: 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response(status=status.HTTP_200_OK)
        response = self.attach_jwt_cookies(response, serializer=serializer)
        response.data = {'status': 'ok'}
        return response

    def remove_tokens_from_response(
        self,
        serializer: serializers.BaseSerializer[Any],
        response_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Remove access and refresh tokens from response body."""
        response_data.pop('refresh', None)
        response_data.pop('access', None)
        user = getattr(serializer, 'user', None)
        if user:
            response_data.update({
                'id': getattr(user, 'id', None),
                'email': getattr(user, 'email', None),
            })
        else:
            response_data.update({
                'id': None,
                'email': None,
            })
        return response_data

    def attach_jwt_cookies(
        self,
        response: Response,
        serializer: serializers.BaseSerializer[Any] | None = None,
        refresh: RefreshToken | None = None,
    ) -> Response:
        """Set JWT cookies based on serializer or refresh token."""
        if serializer:
            access_token = serializer.validated_data.get('access')
            refresh_token = serializer.validated_data.get('refresh')
        else:
            access_token = str(refresh.access_token)  # type: ignore[union-attr]
            refresh_token = str(refresh)
        access_config: CookieConfig = build_cookie_config(
            key=settings.JWT_COOKIE[settings.COOKIE_ACCESS_NAME],
            cookie_value=access_token,
            max_age=int(
                settings.SIMPLE_JWT[
                    settings.ACCESS_LIFETIME_KEY
                ].total_seconds()
            ),
            path=settings.JWT_COOKIE[settings.ACCESS_PATH_KEY],
        )
        refresh_config: CookieConfig = build_cookie_config(
            key=settings.JWT_COOKIE[settings.COOKIE_REFRESH_NAME],
            cookie_value=refresh_token,
            max_age=int(
                settings.SIMPLE_JWT[
                    settings.REFRESH_LIFETIME_KEY
                ].total_seconds()
            ),
            path=settings.JWT_COOKIE[settings.REFRESH_PATH_KEY],
        )
        return self._set_all_cookies(response, access_config, refresh_config)

    def remove_jwt_from_cookie(self) -> Response:
        """Delete JWT from cookie."""
        response = Response(status=status.HTTP_200_OK)
        response = clear_cookie(
            response,
            settings.JWT_COOKIE[settings.COOKIE_ACCESS_NAME],
            path=settings.JWT_COOKIE['ACCESS_PATH'],
        )
        return clear_cookie(
            response,
            settings.JWT_COOKIE[settings.COOKIE_REFRESH_NAME],
            path=settings.JWT_COOKIE['REFRESH_PATH'],
        )

    def _set_all_cookies(
        self,
        response: Response,
        access_config: CookieConfig,
        refresh_config: CookieConfig,
    ) -> Response:
        """Set access and refresh cookies."""
        response = set_cookie(response, access_config)
        return set_cookie(response, refresh_config)
