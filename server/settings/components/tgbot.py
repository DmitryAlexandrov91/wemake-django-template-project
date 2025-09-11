from server.settings.components import config

BOT_TOKEN = config('TG_BOT_TOKEN')
WEBHOOK_SECRET = config('WEBHOOK_SECRET')
WEBHOOK_PATH = config('WEBHOOK_PATH', default='/webhook/')
