import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import BOT_TOKEN
from database.db import create_pool, close_pool
from middlewares.subscription import SubscriptionMiddleware
from handlers import start


async def main():
    logging.basicConfig(level=logging.INFO)

    await create_pool()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Регистрируем middleware на уровне всех апдейтов
    dp.update.middleware(SubscriptionMiddleware())

    # Подключаем роутеры
    dp.include_router(start.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await close_pool()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")