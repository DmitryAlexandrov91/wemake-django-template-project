from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users.drf_spectacular_schemas.schema import (
    password_recovery_schema,
)
from server.apps.users.processing import pass_recovery_processing
from server.apps.users.validators import validate_request


@password_recovery_schema
class PasswordRecoveryAPIView(APIView):
    """Recovers the user password."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        """Handle POST request for password recovery."""
        email = validate_request(request)
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        pass_recovery_processing(email)
        return Response(status=status.HTTP_200_OK)
