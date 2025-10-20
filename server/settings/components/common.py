"""
Django settings for server project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their config, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from datetime import timedelta

from django.utils.translation import gettext_lazy as _

from server.settings.components import BASE_DIR, config

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY = config('DJANGO_SECRET_KEY')

# Application definition:

INSTALLED_APPS: tuple[str, ...] = (
    # Your apps go here:
    'server.apps.users',
    'server.apps.company',
    'server.apps.tgbot',
    'server.apps.surveys',
    # Default django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django-admin:
    'django.contrib.admin',
    'django.contrib.admindocs',
    # Security:
    'axes',
    # Health checks:
    # You may want to enable other checks as well,
    # see: https://github.com/KristianOellegaard/django-health-check
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    # DRF apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',
    'drf_spectacular',
)

MIDDLEWARE: tuple[str, ...] = (
    # Logging:
    'server.settings.components.logging.LoggingContextVarsMiddleware',
    # Content Security Policy:
    'csp.middleware.CSPMiddleware',
    # Django:
    'django.middleware.security.SecurityMiddleware',
    # django-permissions-policy
    'django_permissions_policy.PermissionsPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Axes:
    'axes.middleware.AxesMiddleware',
)

AUTH_USER_MODEL = 'users.CustomUser'

ROOT_URLCONF = 'server.urls'

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DJANGO_DATABASE_HOST'),
        'PORT': config('DJANGO_DATABASE_PORT', cast=int),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', cast=int, default=60),
        'OPTIONS': {
            'pool': True,
            'connect_timeout': 10,
            'options': '-c statement_timeout=15000ms',
            # consider using 'isolation_level' set to 'serializable'
        },
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

LOCALE_PATHS = ('locale/',)

USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Templates
# https://docs.djangoproject.com/en/5.2/ref/templates/api

TEMPLATES = [
    {
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Contains plain text templates, like `robots.txt`:
            BASE_DIR.joinpath('server', 'common', 'django', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                # Default template context processors:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]


# Media files
# Media root dir is commonly changed in production
# (see development.py and production.py).
# https://docs.djangoproject.com/en/5.2/topics/files/

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.joinpath('media')


# Django authentication system
# https://docs.djangoproject.com/en/5.2/topics/auth/

AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]


# Security
# https://docs.djangoproject.com/en/5.2/topics/security/

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = 'DENY'

# https://docs.djangoproject.com/en/3.0/ref/middleware/#referrer-policy
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
SECURE_REFERRER_POLICY = 'same-origin'

# https://github.com/adamchainz/django-permissions-policy#setting
PERMISSIONS_POLICY: dict[str, str | list[str]] = {}


# Timeouts
# https://docs.djangoproject.com/en/5.2/ref/settings/#std:setting-EMAIL_TIMEOUT

EMAIL_TIMEOUT = 5

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'server.apps.users.auth.CookieJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': (
        'server.apps.surveys.paginators.CustomPaginator'
    ),
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Cookie
EXCEPTION_DETAIL_ATRR = 'detail'
COOKIE_REFRESH_NAME = 'REFRESH_NAME'
COOKIE_ACCESS_NAME = 'ACCESS_NAME'
REFRESH_LIFETIME_KEY = 'REFRESH_TOKEN_LIFETIME'
ACCESS_LIFETIME_KEY = 'ACCESS_TOKEN_LIFETIME'
ACCESS_PATH_KEY = 'ACCESS_PATH'
REFRESH_PATH_KEY = 'REFRESH_PATH'

DEBUG = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'https://localhost',
]
JWT_COOKIE = {
    COOKIE_ACCESS_NAME: 'access_token',
    COOKIE_REFRESH_NAME: 'refresh_token',
    'SAMESITE': 'Lax',
    'SECURE': not DEBUG,
    'HTTPONLY': True,
    'REFRESH_PATH': '/api/auth/refresh',
    'ACCESS_PATH': '/',
}

SIMPLE_JWT = {
    'SIGNING_KEY': os.getenv('JWT_SIGNING_KEY', SECRET_KEY),
    'ALGORITHM': 'HS256',
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.getenv('JWT_ACCESS_MIN', '15'))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.getenv('JWT_REFRESH_DAYS', '7'))
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': False,
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1


SPECTACULAR_SETTINGS = {
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_AUTHENTICATION': [],
}

DEFAULT_USER_STAT_PERIOD = 50
