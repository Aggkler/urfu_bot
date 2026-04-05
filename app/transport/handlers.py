import telebot

def register_handlers(bot: telebot.TeleBot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message: telebot.types.Message) -> None:
        bot.send_message(
            chat_id=message.chat.id,
            text=f'Приветствую тебя в боте!\nСкоро твою заявку одобрят и ты получишь доступ к материалу'
        )
