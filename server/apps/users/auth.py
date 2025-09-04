from typing import final, override

from django.conf import settings
from django.http import HttpRequest
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import AuthUser
from rest_framework_simplejwt.tokens import Token


@final
class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads the token from HttpOnly cookie.

    This allows using JWTs stored in cookies instead of sending them in
    the Authorization header, which is useful for web clients
    where cookies provide better security (HttpOnly, Secure, SameSite).

    Inherits from `rest_framework_simplejwt.authentication.JWTAuthentication`.
    """

    @override
    def authenticate(
        self, request: HttpRequest
    ) -> tuple[AuthUser, Token] | None:
        """
        Attempt to authenticate the request using either.

        1. The Authorization header (default JWT behavior).
        2. The access token stored in an HttpOnly cookie.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            tuple(user, validated_token) if authentication succeeds,
            or None if no token is provided.

        Raises:
            AuthenticationFailed: If the token is invalid
            or cannot be validated.
        """
        raw_token = request.COOKIES.get(settings.JWT_COOKIE['ACCESS_NAME'])
        try:
            validated_token = self.get_validated_token(
                raw_token.encode('utf-8')  # type: ignore[union-attr]
            )
        except Exception as error:
            raise exceptions.AuthenticationFailed(
                'Invalid token', code='invalid_token'
            ) from error
        return self.get_user(validated_token), validated_token  # type: ignore[return-value]
