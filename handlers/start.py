from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.types import CallbackQuery

from database.db import get_or_create_member

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    full_name = user.full_name or ''

    await get_or_create_member(
        telegram_id=user.id,
        tg_nick=user.username,
        full_name=full_name,
    )

    await message.answer(
        f"Привет, {full_name}!\n"
        "Вы успешно прошли проверку. Бот доступен для вас!"
    )


@router.message()
async def echo(message: Message):
    await message.answer("Команда не распознана. Используйте /start")

@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):
    print("Callback received")