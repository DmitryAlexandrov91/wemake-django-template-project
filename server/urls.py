"""
Main URL mapping configuration file.

Include other URLConfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This example uses Django's default media
files serving technique in development.
"""

from django import conf, contrib
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include, path
from django.views.generic import TemplateView
from health_check import urls as health_urls

from server.apps.company import urls as company_urls
from server.apps.surveys import urls as surveys_urls
from server.apps.tgbot.views import TelegramWebhookView
from server.apps.users import urls as users_urls
from server.apps.users import views
from server.di import resolve

contrib.admin.autodiscover()

settings = resolve(conf.LazySettings)


urlpatterns = [
    # Apps:
    path(
        'password-recovery',
        views.PasswordRecoveryAPIView.as_view(),
        name='password-recovery',
    ),
    # Health checks:
    path('health/', include(health_urls)),
    # django-admin:
    path('admin/doc/', include(admindocs_urls)),
    path('admin/', contrib.admin.site.urls),
    # Users auth
    path('', include(users_urls)),
    # Surveys API
    path('api/', include(surveys_urls)),
    # Company app API
    path('api/', include(company_urls)),
    # Text and xml static files:
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='common/txt/robots.txt',
            content_type='text/plain',
        ),
    ),
    path(
        'humans.txt',
        TemplateView.as_view(
            template_name='common/txt/humans.txt',
            content_type='text/plain',
        ),
    ),
    # Telegram webhook
    path(
        settings.WEBHOOK_PATH.lstrip('/'),
        TelegramWebhookView.as_view(),
        name='webhook',
    ),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns = [
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include(debug_toolbar.urls)),
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
