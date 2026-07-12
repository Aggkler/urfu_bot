from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_return_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Стартовое меню',
                callback_data='start_menu',)
            ]
        ]
    )