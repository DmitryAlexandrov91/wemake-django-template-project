import telebot

from server.di import resolve


def test_inject_tg_registers_telebot() -> None:
    """Test inject_tg."""
    bot1 = resolve(telebot.TeleBot)
    bot2 = resolve(telebot.TeleBot)
    assert bot1 is bot2
    assert isinstance(bot1, telebot.TeleBot)
    assert bot1.token == bot2.token
