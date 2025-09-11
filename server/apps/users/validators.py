from django.core.validators import validate_email
from rest_framework.request import Request


def validate_request(request: Request) -> str:
    """Check and return a valid email in request data."""
    email = request.data.get('email')
    validate_email(email)
    return str(email)
