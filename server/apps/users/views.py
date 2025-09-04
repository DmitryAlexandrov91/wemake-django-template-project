from typing import Any, override

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenViewBase

from server.apps.users import auth, serializers, services
from server.di import resolve


class CookieTokenObtainPairView(TokenViewBase):
    """
    View to handle user login, issue JWT tokens, and store them in cookies.

    Returns only user info in the response body. Tokens are stored in
    HttpOnly cookies for security.
    """

    serializer_class = serializers.CookieTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)  # type: ignore[assignment]

    @override
    def post(
        self,
        request: Request,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Response:
        """
        Handle POST requests for login.

        Args:
            request (Request): The HTTP request containing 'email' and
                'password'.
            *args: Additional positional arguments passed by DRF.
            **kwargs: Additional keyword arguments passed by DRF.

        Returns:
            Response: DRF Response with user info and JWT tokens set
            in cookies.
        """
        serializer = self.get_serializer(data=request.data)
        return resolve(services.AuthService).authenticate_user(serializer)


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


class LogoutView(APIView):
    """Logout view that clears both access and refresh token cookies."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        """
        Handle POST requests for logout.

        Returns:
            Response with cookies cleared.
        """
        return resolve(services.AuthService).remove_jwt_from_cookie()
