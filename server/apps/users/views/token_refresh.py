from typing import Any, override

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenViewBase

from server.apps.users import auth, services
from server.di import resolve


class CookieTokenRefreshView(TokenViewBase):
    """View to handle access token refresh using the refresh token cookie."""

    serializer_class = TokenRefreshSerializer
    permission_classes = (permissions.AllowAny,)  # type: ignore[assignment]
    authentication_classes = (auth.CookieJWTAuthentication,)  # type: ignore[assignment]

    @override
    def post(
        self,
        request: Request,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Response:
        """
        Refresh the access token using the refresh token cookie.

        Returns:
            Response with new access token in cookies.
        """
        refresh_token = request.COOKIES.get(
            settings.JWT_COOKIE[settings.COOKIE_REFRESH_NAME]
        )
        if not refresh_token:
            return Response(
                {settings.EXCEPTION_DETAIL_ATRR: 'Missing refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = self.get_serializer(data={'refresh': refresh_token})
        return resolve(services.AuthService).refresh_access_token(serializer)
