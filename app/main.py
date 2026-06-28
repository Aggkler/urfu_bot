import asyncio
import logging

from aiogram import Bot, Dispatcher

import db
from config.settings import BOT_TOKEN
from handlers import start, invite


async def main():
    logging.basicConfig(level=logging.INFO)

    await db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(invite.router)

    try:
        await dp.start_polling(bot)
    finally:
        await db.close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())