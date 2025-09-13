from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users.processing import pass_recovery_processing


class PasswordRecoveryAPIView(APIView):
    """Recovers the user password."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        """Handle POST request for password recovery."""
        pass_recovery_processing(request)
        return Response(status=status.HTTP_200_OK)
