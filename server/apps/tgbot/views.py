from http import HTTPStatus

from django.conf import LazySettings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from server.apps.tgbot.usecases import ProcessTelegramUpdate
from server.di import resolve

settings = resolve(LazySettings)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """Webhook telegram responses from bot."""

    http_method_names = ('post',)

    def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        """Handle POST and transfer data to bot."""
        secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')

        if secret_token != settings.WEBHOOK_SECRET:
            return HttpResponseForbidden('Invalid secret token')

        process_update = resolve(ProcessTelegramUpdate)
        process_update(request.body)

        return HttpResponse('ok', status=HTTPStatus.OK)
