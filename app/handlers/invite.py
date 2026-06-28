import secrets
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

import db

router = Router()


@router.message(Command("invite"))
async def create_invite_link(message: Message, bot: Bot):
    tg_id = message.from_user.id

    # Только зарегистрированные могут приглашать
    member = await db.get_member(tg_id)
    if not member:
        await message.answer("🔒 У вас нет доступа к боту.")
        return

    # Генерируем уникальный код
    code = secrets.token_urlsafe(8)
    await db.create_invite(code, member["id"])

    bot_user = await bot.me()
    link = f"https://t.me/{bot_user.username}?start={code}"

    await message.answer(
        "🔗 Ваша одноразовая ссылка-приглашение:\n"
        f"`{link}`\n\n"
        "Её можно использовать только **один раз**.",
        parse_mode="Markdown"
    )