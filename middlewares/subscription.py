from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config.settings import CHANNEL_ID, ADMIN_IDS
from keyboards.subscription_kb import get_subscription_keyboard
from database.db import update_subscription_status, is_user_banned


SUBSCRIBED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        bot = data["bot"]

        # Определяем пользователя и объект для ответа
        user = None
        message = None
        callback = None

        if event.message:
            user = event.message.from_user
            message = event.message
        elif event.callback_query:
            user = event.callback_query.from_user
            callback = event.callback_query
            message = event.callback_query.message
        else:
            return await handler(event, data)

        if user is None:
            return await handler(event, data)

        # Админы проходят без проверки
        if user.id in ADMIN_IDS:
            return await handler(event, data)

        # Проверка бана
        if await is_user_banned(user.id):
            if message:
                await message.answer("Вы заблокированы в этом боте.")
            return  # прерываем обработку

        # Пропускаем сам callback проверки подписки до проверки
        # (чтобы пользователь мог нажать "Я подписался")
        is_check_callback = (
            callback is not None and callback.data == "check_subscription"
        )

        # Проверяем подписку через Telegram API
        is_subscribed = await self._check_subscription(bot, user.id)

        # Обновим статус в БД
        await update_subscription_status(user.id, is_subscribed)

        if not is_subscribed:
            text = (
                "Для доступа к боту необходимо подписаться на наш канал.\n\n"
                "Подпишитесь и нажмите кнопку «Я подписался»."
            )
            if is_check_callback:
                await callback.answer(
                    "Вы всё ещё не подписаны", show_alert=True
                )
            elif message:
                await message.answer(text, reply_markup=get_subscription_keyboard())
            return  # прерываем — дальше не пускаем

        # Если подписан и нажал "Я подписался"
        if is_check_callback:
            await callback.answer("Спасибо за подписку!", show_alert=True)
            await callback.message.answer(
                "Доступ открыт! Используйте /start чтобы начать."
            )
            return

        return await handler(event, data)

    @staticmethod
    async def _check_subscription(bot, user_id: int) -> bool:
        try:
            member = await bot.get_chat_member(
                chat_id=CHANNEL_ID, user_id=user_id
            )
            return member.status in SUBSCRIBED_STATUSES
        except Exception:
            # Пользователь не найден / бот не админ канала и т.п.
            return False