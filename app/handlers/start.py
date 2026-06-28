from aiogram import Router, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import db
from config.settings import ADMIN_IDS

router = Router()


async def notify_inviter(bot: Bot, inviter_member: dict, new_member: dict):
    """Отправляет пригласившему уведомление о новой регистрации."""
    if not inviter_member or not inviter_member["telegram_id"]:
        return

    nick = new_member["tg_nick"]
    nick_str = f"@{nick}" if nick else "без username"
    name = new_member["full_name"] or "Без имени"

    text = (
        "🎉 По вашему приглашению зарегистрировался новый участник!\n\n"
        f"👤 Имя: {name}\n"
        f"🔗 Username: {nick_str}"
    )

    try:
        await bot.send_message(inviter_member["telegram_id"], text)
    except (TelegramForbiddenError, TelegramBadRequest):
        # пригласивший заблокировал бота или чат недоступен — игнорируем
        pass


@router.message(CommandStart(deep_link=True))
async def start_with_invite(message: Message, command: CommandObject, bot: Bot):
    """Вход по deep-link с инвайт-кодом."""
    tg_id = message.from_user.id
    code = command.args

    # Уже зарегистрирован?
    member = await db.get_member(tg_id)
    if member:
        await message.answer("Вы уже зарегистрированы 👋")
        return

    # Проверяем инвайт
    invite = await db.get_invite(code)
    if not invite:
        await message.answer("❌ Приглашение не найдено.")
        return
    if invite["is_used"]:
        await message.answer("❌ Это приглашение уже использовано.")
        return

    # Создаём пользователя
    new_member = await db.create_member(
        telegram_id=tg_id,
        tg_nick=message.from_user.username,
        full_name=message.from_user.full_name or "",
        role="student",
    )

    # Атомарно закрываем инвайт
    used = await db.use_invite(code, new_member["id"])
    if not used:
        await message.answer("❌ Приглашение только что было использовано.")
        return

    await message.answer(
        "✅ Добро пожаловать! Вы успешно зарегистрированы.\n"
        "Теперь вы можете приглашать других через /invite"
    )

    # Уведомляем пригласившего
    inviter = await db.get_member_by_id(invite["inviter_id"])
    await notify_inviter(bot, inviter, dict(new_member))


@router.message(CommandStart())
async def start_no_invite(message: Message):
    """Вход без инвайта."""
    tg_id = message.from_user.id
    member = await db.get_member(tg_id)

    if member:
        await message.answer(f"С возвращением, {member['full_name'] or 'друг'}! 👋")
        return

    # Админы заходят без приглашения
    if tg_id in ADMIN_IDS:
        await db.create_member(
            telegram_id=tg_id,
            tg_nick=message.from_user.username,
            full_name=message.from_user.full_name or "",
            role="admin",
        )
        await message.answer("Вы вошли как администратор")
        return

    await message.answer(
        "🔒 Доступ к боту только по приглашению.\n"
        "Попросите участника прислать вам ссылку-приглашение."
    )