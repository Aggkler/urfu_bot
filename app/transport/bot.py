import telebot

from app.transport.handlers import register_handlers
from config import settings

def main():
    bot = telebot.TeleBot(settings.BOT_TOKEN)
    register_handlers(bot)
    bot.infinity_polling()

if __name__ == "__main__":
    main()