from typing import override

from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):  # type: ignore[no-untyped-call]
    """OpenAPI schema for CookieJWTAuthentication."""

    target_class = 'server.apps.users.auth.CookieJWTAuthentication'
    name = 'CookieJWTAuthentication'
    priority = 1

    @override
    def get_security_definition(
        self,
        auto_schema: AutoSchema,
    ) -> dict[str, str]:
        """Return OpenAPI security definition for the cookie."""
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': settings.JWT_COOKIE['ACCESS_NAME'],
        }
