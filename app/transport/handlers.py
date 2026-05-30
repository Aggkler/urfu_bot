import html

import telebot

from app.db.repository import (
    save_user,
    get_user_role,
    set_user_role_by_id,
    set_user_role_by_nick,
    get_users,
    create_material,
    get_materials,
    get_material_by_id,
    get_student_ids,
    get_all_materials
)
from config import settings


def normalize_nick(username: str | None):
    if not username:
        return None

    return username.replace('@', '').lower().strip()


def get_full_name(message: telebot.types.Message):
    first_name = message.from_user.first_name or ''
    last_name = message.from_user.last_name or ''
    return f'{first_name} {last_name}'.strip()


def get_message_text(message: telebot.types.Message):
    return message.text or message.caption or ''


def get_args(message: telebot.types.Message):
    text = get_message_text(message)
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        return ''

    return parts[1].strip()


def is_admin(user_id: int):
    return user_id in settings.ADMIN_IDS


def has_access(role: str | None):
    return role in ['student', 'teacher', 'admin']


def can_publish(role: str | None):
    return role in ['teacher', 'admin']


def get_file_data(message: telebot.types.Message):
    if message.document:
        return message.document.file_id, 'document'

    if message.photo:
        return message.photo[-1].file_id, 'photo'

    if message.video:
        return message.video.file_id, 'video'

    if message.audio:
        return message.audio.file_id, 'audio'

    return None, 'text'


def parse_publish_args(args: str, has_file: bool):
    args = args.strip()

    if '|' in args:
        title, body = args.split('|', maxsplit=1)
        return title.strip(), body.strip()

    if has_file:
        return args or 'Материал', ''

    return 'Материал', args


def send_material(bot: telebot.TeleBot, chat_id: int, material):
    title = html.escape(material['title'])
    body = html.escape(material['body'] or '')

    text = f'<b>Материал #{material["id"]}</b>\n\n<b>{title}</b>'

    if body:
        text += f'\n\n{body}'

    file_id = material['file_id']
    file_type = material['file_type']

    if not file_id:
        bot.send_message(chat_id, text, parse_mode='HTML')
        return

    caption = text[:1000]

    if file_type == 'document':
        bot.send_document(chat_id, file_id, caption=caption, parse_mode='HTML')

    elif file_type == 'photo':
        bot.send_photo(chat_id, file_id, caption=caption, parse_mode='HTML')

    elif file_type == 'video':
        bot.send_video(chat_id, file_id, caption=caption, parse_mode='HTML')

    elif file_type == 'audio':
        bot.send_audio(chat_id, file_id, caption=caption, parse_mode='HTML')

    else:
        bot.send_message(chat_id, text, parse_mode='HTML')

    if len(text) > 1000:
        bot.send_message(chat_id, text, parse_mode='HTML')


def register_handlers(bot: telebot.TeleBot):

    @bot.message_handler(commands=['start'])
    def start_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        tg_nick = normalize_nick(message.from_user.username)
        full_name = get_full_name(message)

        save_user(user_id, tg_nick, full_name)

        if is_admin(user_id):
            set_user_role_by_id(user_id, 'admin')

        role = get_user_role(user_id)

        if role == 'student':
            text = (
                'Привет! Тебе открыт доступ к учебным материалам.\n\n'
                'Команды:\n'
                '/materials — список материалов\n'
                '/material 1 — открыть материал по номеру'
            )

        elif role == 'teacher':
            text = (
                'Привет, преподаватель!\n\n'
                'Команды:\n'
                '/publish Название | Текст материала — опубликовать материал\n'
                '/materials — список материалов\n'
                '/users — список пользователей',
            )

        elif role == 'admin':
            text = (
                'Привет, администратор!\n\n'
                'Команды:\n'
                '/setrole @username student — назначить ученика\n'
                '/setrole @username teacher — назначить преподавателя\n'
                '/publish Название | Текст материала — опубликовать материал\n'
                '/materials — список материалов\n'
                '/users — список пользователей\n'
            )

        else:
            text = (
                'Приветствую тебя в боте!\n\n'
                'Твоя заявка создана. '
                'Скоро преподаватель или администратор одобрит доступ к материалам.'
            )

        bot.send_message(message.chat.id, text)


    @bot.message_handler(commands=['myid'])
    def my_id_handler(message: telebot.types.Message) -> None:
        bot.send_message(
            message.chat.id,
            f'Твой Telegram ID: {message.from_user.id}'
        )

    @bot.message_handler(commands=['role'])
    def role_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        tg_nick = normalize_nick(message.from_user.username)
        full_name = get_full_name(message)

        save_user(user_id, tg_nick, full_name)

        if is_admin(user_id):
            set_user_role_by_id(user_id, 'admin')

        role = get_user_role(user_id)

        bot.send_message(
            message.chat.id,
            f'Твоя роль: {role}'
        )


    @bot.message_handler(commands=['setrole'])
    def set_role_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id

        if not is_admin(user_id):
            bot.send_message(
                message.chat.id,
                'Назначать роли может только администратор.'
            )
            return

        args = get_args(message).split()

        if len(args) != 2:
            bot.send_message(
                message.chat.id,
                'Формат команды:\n'
                '/setrole @username student\n\n'
                'Доступные роли:\n'
                'student — ученик\n'
                'teacher — преподаватель\n'
                'admin — администратор'
            )
            return

        username = normalize_nick(args[0])
        role = args[1].lower()

        if role not in ['student', 'teacher', 'admin']:
            bot.send_message(
                message.chat.id,
                'Такой роли нет. Используй: student, teacher, admin.'
            )
            return

        success = set_user_role_by_nick(username, role)

        if not success:
            bot.send_message(
                message.chat.id,
                'Пользователь не найден.\n'
                'Попроси его сначала написать боту команду /start.'
            )
            return

        bot.send_message(
            message.chat.id,
            f'Пользователю @{username} назначена роль: {role}'
        )


    @bot.message_handler(commands=['approve'])
    def approve_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id

        if not is_admin(user_id):
            bot.send_message(
                message.chat.id,
                'Одобрять заявки может только администратор.'
            )
            return

        username = normalize_nick(get_args(message))

        if not username:
            bot.send_message(
                message.chat.id,
                'Формат команды:\n/approve @username'
            )
            return

        success = set_user_role_by_nick(username, 'student')

        if not success:
            bot.send_message(
                message.chat.id,
                'Пользователь не найден. Он должен сначала написать /start.'
            )
            return

        bot.send_message(
            message.chat.id,
            f'Пользователь @{username} одобрен как ученик.'
        )


    @bot.message_handler(commands=['users'])
    def users_handler(message: telebot.types.Message) -> None:
        role = get_user_role(message.from_user.id)

        if role not in ['teacher', 'admin']:
            bot.send_message(
                message.chat.id,
                'Список пользователей доступен только преподавателю или администратору.'
            )
            return

        users = get_users()

        if not users:
            bot.send_message(message.chat.id, 'Пользователей пока нет.')
            return

        text = '<b>Пользователи:</b>\n\n'

        for user in users:
            nick = f"@{user['tg_nick']}" if user['tg_nick'] else 'без ника'
            user_role = user['role']
            text += f'{html.escape(nick)} — <b>{html.escape(user_role)}</b>\n'

        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML'
        )

    @bot.message_handler(
        func=lambda message: get_message_text(message).startswith('/publish'),
        content_types=['text', 'document', 'photo', 'video', 'audio']
    )
    def publish_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        role = get_user_role(user_id)

        if not can_publish(role):
            bot.send_message(
                message.chat.id,
                'Публиковать материалы может только преподаватель или администратор.'
            )
            return

        args = get_args(message)

        file_id, file_type = get_file_data(message)
        has_file = file_id is not None

        if not args and not has_file:
            bot.send_message(
                message.chat.id,
                'Формат публикации:\n\n'
                '/publish Название материала | Текст материала\n\n'
                'Или прикрепи файл/фото/видео и в подписи напиши:\n'
                '/publish Название материала | Описание'
            )
            return

        title, body = parse_publish_args(args, has_file)

        if not title:
            bot.send_message(
                message.chat.id,
                'Название материала не должно быть пустым.'
            )
            return

        material_id = create_material(
            title=title,
            body=body,
            teacher_telegram_id=user_id,
            file_id=file_id,
            file_type=file_type
        )

        if material_id is None:
            bot.send_message(
                message.chat.id,
                'Ошибка: преподаватель не найден в базе. Напиши /start и попробуй снова.'
            )
            return

        material = get_material_by_id(material_id)

        student_ids = get_student_ids()
        success_count = 0
        error_count = 0

        for student_id in student_ids:
            try:
                send_material(bot, student_id, material)
                success_count += 1
            except Exception:
                error_count += 1

        bot.send_message(
            message.chat.id,
            f'Материал опубликован.\n\n'
            f'Номер материала: {material_id}\n'
            f'Тип материала: {file_type}\n'
            f'Отправлено ученикам: {success_count}\n'
            f'Ошибок отправки: {error_count}'
        )


    @bot.message_handler(commands=['materials'])
    def materials_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        role = get_user_role(user_id)

        if not has_access(role):
            bot.send_message(
                message.chat.id,
                'У тебя пока нет доступа к материалам.'
            )
            return

        materials = get_materials()

        if not materials:
            bot.send_message(message.chat.id, 'Материалов пока нет.')
            return

        text = '<b>Список материалов:</b>\n\n'

        for material in materials:
            material_id = material['id']
            title = html.escape(material['title'])
            # created_at = material['created_at'].strftime('%d.%m.%Y %H:%M')
            # text += f'#{material_id} — {title} — {created_at}\n'
            text += f'ID: {material_id} — {title}\n'

        text += '\nЧтобы открыть материал, напиши:\n/material 1'

        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML'
        )


    @bot.message_handler(commands=['material'])
    def material_handler(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        role = get_user_role(user_id)

        if not has_access(role):
            bot.send_message(
                message.chat.id,
                'У тебя пока нет доступа к материалам.'
            )
            return

        args = get_args(message)

        if not args.isdigit():
            bot.send_message(
                message.chat.id,
                'Укажи номер материала.\n\n'
                'Пример:\n/material 1'
            )
            return

        material = get_material_by_id(int(args))

        if not material:
            bot.send_message(message.chat.id, 'Материал не найден.')
            return

        send_material(bot, message.chat.id, material)