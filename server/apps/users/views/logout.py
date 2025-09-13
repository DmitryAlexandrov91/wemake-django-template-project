from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users import services
from server.di import resolve


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
