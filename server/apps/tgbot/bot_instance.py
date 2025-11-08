from telebot import TeleBot

from server.di import resolve

bot: TeleBot = resolve(TeleBot)
