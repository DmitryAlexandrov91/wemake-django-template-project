import telebot
from django.conf import LazySettings, settings

from server.di import resolve


def test_inject_tg_registers_telebot() -> None:
    """Test inject_tg."""
    bot1 = resolve(telebot.TeleBot)
    bot2 = resolve(telebot.TeleBot)
    assert bot1 is bot2
    assert isinstance(bot1, telebot.TeleBot)
    assert bot1.token == bot2.token


def test_inject_settings() -> None:
    """Test inject_settings."""
    settings_from_di = resolve(LazySettings)

    assert settings_from_di is settings
