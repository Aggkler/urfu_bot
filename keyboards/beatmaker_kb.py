from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_beatmaker_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='NEST',
                callback_data="get_nest",)
            ],
            [InlineKeyboardButton(
                text='VisaGangBeatz',
                callback_data="get_visagangbeatz",)
            ],
            [InlineKeyboardButton(
                text='Kennycarter & young dexn',
                callback_data="get_kennycarter",
            ), InlineKeyboardButton(
                text='Slava Marlow',
                callback_data="get_slavamarlow",
            )],
            [InlineKeyboardButton(
                text='Treepside',
                callback_data="get_treepside",
            )]
        ]

    )