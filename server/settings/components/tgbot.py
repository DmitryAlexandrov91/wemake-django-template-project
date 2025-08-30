import os
import sys

from server.settings.components import config

is_test_mode = (
    'pytest' in sys.modules
    or 'test' in sys.argv
    or 'test' in os.environ.get('DJANGO_SETTINGS_MODULE', '')
    or os.environ.get('PYTEST_CURRENT_TEST')
)


if is_test_mode:
    BOT_TOKEN = '1234567890:AAFakeTokenForTesting123456789'  # noqa: S105
else:
    BOT_TOKEN = config('TG_BOT_TOKEN')
