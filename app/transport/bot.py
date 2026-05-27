import telebot

from app.db.db_connection import init_pool, init_db
from app.transport.handlers import register_handlers
from config import settings


def main():
    init_pool()
    init_db()

    bot = telebot.TeleBot(settings.BOT_TOKEN)
    register_handlers(bot)

    print('Бот запущен...')
    bot.infinity_polling()


if __name__ == "__main__":
    main()