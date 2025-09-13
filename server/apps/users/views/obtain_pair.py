from typing import Any, override

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from server.apps.users import serializers, services
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
