from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import CHANNEL_USERNAME


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⌛ Подписаться на канал",
                    url=f"https://t.me/{CHANNEL_USERNAME}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💚 Я подписался",
                    callback_data="check_subscription",
                )
            ],
        ]
    )
