import asyncio

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram import F

from database.db import get_or_create_member, is_admin_member
from keyboards.beatmaker_kb import get_beatmaker_keyboard
from keyboards.return_kb import get_return_keyboard

router = Router()
lock = asyncio.Lock()


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
        text=f"Привет, {full_name}!\nВы успешно прошли проверку. Бот доступен для вас!",
        reply_markup=get_return_keyboard()
    )

@router.callback_query(F.data == 'get_nest')
async def get_nest(callback: CallbackQuery):
    await callback.answer("NEST")
    lst_word_nest = ['<b>Nest</b>\n\nРыжков Константин Анатольевич (родился 27 марта 2003 года)',
                ' - саунд-продюсер родом из Екатеринбурга, работавший с такими артистами, как <b>Yeat</b>,',
                '<b>OG Buda</b>, <b>Платина</b> и другими.\n\n','<b>Социальные сети:</b>\n',
                'Telegram: <a href="https://t.me/nestxvi">nest.me</a>\n',
                'Twitch: <a href="www.twitch.tv/nestxvi">nest.tv</a>\n']
    await callback.message.answer_photo(
        photo='AgACAgIAAxkBAAIBbmpRnd0wA1wspYkbLSxGHeKib81WAALUFWsbWbWRSvEyisnTSBFYAQADAgADeAADPAQ',
        caption=''.join(lst_word_nest),
        reply_markup=get_return_keyboard()
    )

@router.callback_query(F.data == 'get_visagangbeatz')
async def get_visagangbeatz(callback: CallbackQuery):
    await callback.answer("VisaGangBeatz")
    lst_word_vgb = ['<b>VisaGangBeatz</b>\n\nРудиков Александр Сергеевич (родился 16 апреля 2002 года)',
                '— мультиплатиновый продюсер и звукорежиссёр из Москвы. Состоит в творческом объединении ',
               '<b>DooMasters</b>.\n\n', '<b>Социальные сети:</b>\n',
                'Telegram: <a href="https://t.me/visagangbeatzofficial">visa.me</a>\n',
                'Twitch: <a href="https://www.twitch.tv/visagangbeatzz">visa.tv</a>\n',
                'YouTube: <a href="https://www.youtube.com/@visagangbeatz">visa.youtube</a>',
                ]
    await callback.message.answer_photo(
        photo='AgACAgIAAxkBAAIBU2pRdcWlpyiW3qcJ9oXWPwAB1P9KhQACuSBrG1m1iUpux-u_gGLPIQEAAwIAA3kAAzwE',
        caption=''.join(lst_word_vgb),
        reply_markup=get_return_keyboard()
    )
@router.callback_query(F.data == 'get_kennycarter')
async def get_kennycarter(callback: CallbackQuery):
    await callback.answer("Kennycarter & young dexn")
    lst_word_kenny = ['<b>Kennycarter & young dexn</b>\n\nПаустовойт Богдан Сергеевич и Шаронов Денис Александрович ',
                      '- российские платиновые продюсеры\nwork w/ ',
                      'pepel nahudi, madk1d, newlightchild, heronwater, шайни, xxxmanera, deathmarried, huzzy b...\n\n',
                      '<b>Социальные сети:</b>\n',
                      'Telegram: <a href="https://t.me/KXDbeats">kennycarter&youngdexn.me</a>']
    await callback.message.answer_photo(
        photo='AgACAgIAAxkBAAIBWGpRkr9Ql0ygDYx2UakGsodoxE45AALLFWsbWbWRSkRnKrPDqxwqAQADAgADeAADPAQ',
        caption=''.join(lst_word_kenny),
        reply_markup=get_return_keyboard()
    )

@router.callback_query(F.data == 'get_slavamarlow')
async def get_slavamarlow(callback: CallbackQuery):
    await callback.answer("Slava Marlow")
    lst_word_slava = ['<b>Slava Marlow</b>\n\nГотлиб Артём Артёмович (родился 27 октября 1999 года в Новосибирске) ',
                      '— российский музыкальный исполнитель, продюсер, звукорежиссёр, дизайнер и блогер\n\n',
                      '<b>Социальные сети:</b>\n',
                      'Telegram: <a href="https://t.me/slavamarlow">SlavaMarlow.me</a>\n',
                      'YouTube: <a href="https://www.youtube.com/@slavamarlow">SlavaMarlow.youtube</a>'
                      ]
    await callback.message.answer_photo(
        photo='AgACAgIAAxkBAAIBW2pRmD6CONyRtmDKN2IP0LjZJkxfAALOFWsbWbWRSuLmm9GeShGSAQADAgADeAADPAQ',
        caption=''.join(lst_word_slava),
        reply_markup=get_return_keyboard()
    )

@router.callback_query(F.data == 'get_treepside')
async def get_treepside(callback: CallbackQuery):
    await callback.answer("Treepside")
    lst_word_treepside = ['<b>Treepside</b>\n\nЕгор Юрьевич Ковалёв (родился 14 марта 1999 года)',
                          '— продюсер и звукоинженер. Первую большую популярность получил благодаря ',
                          'ремиксу на трек Платины — «Валентина».\n', 'work w/ OG Buda, MAYOT, uglystephan, ',
                          'BUSHIDO ZHO, PINQ, SQWORE, ...\n\n', '<b>Социальные сети:</b>\n',
                          'Telegram: <a href="https://t.me/@treepside">treepside.me</a>\n',
                          'Soundcloud: <a href="https://soundcloud.com/treepside">treepside.sound</a>']
    await callback.message.answer_photo(
        photo='AgACAgIAAxkBAAIBb2pRngyP-kye7E6TEGCxQkVTi4ePAALVFWsbWbWRSj49bZgZV9a7AQADAgADeAADPAQ',
        caption=''.join(lst_word_treepside),
        reply_markup=get_return_keyboard()
    )

@router.message(F.photo)
async def get_photo(message: Message):
    # Берем фотографию максимального размера
    photo = message.photo[-1]

    print(photo.file_id)
    print(photo.file_unique_id)

@router.message(F.document and F.caption.lower().startswith("/create"))
async def get_document(message: Message):
    async with lock:
        is_admin = await is_admin_member(message.from_user.id)
        if is_admin:
            print(message.caption)
            document = message.document
            print(f'file id - {document.file_id}')
            print(f'file unique id - {document.file_unique_id}')
            print(f'name file - {document.file_name}')


@router.message()
async def echo(message: Message):
    await message.answer("Команда не распознана.\nИспользуйте /start")
    print(message.entities)  # Убрать потом
    print(message)  # Убрать потом

@router.callback_query()
async def handler(callback: CallbackQuery):
    if callback.data == "start_menu":
        await callback.message.answer(
            "Выберите подходящий пак:",
            reply_markup=get_beatmaker_keyboard()
        )
    print(callback.entities)  # Убрать потом
