from BotUser.utils.keyboard_helper import get_main_keyboard, get_settings_keyboard
from utils import db_connector
from utils.db_connector import increment_answers
from utils.logger import get_logger
from BotUser.bot_user import Botuser
from utils.scheduler import prepare_first_notification

log = get_logger("menu_helper")


def add_user(bot, message):
    user = Botuser(message.chat.id)
    keyboard = get_main_keyboard()
    log.info(f"{user.check_auth()}")
    if user.check_auth():
        message_text = db_connector.get_message_text_by_id(3)
        bot.send_message(user.uid, message_text, reply_markup=keyboard)

    else:
        user.add_user()
        message_text = db_connector.get_message_text_by_id(3)
        bot.send_message(user.uid, message_text, reply_markup=keyboard)
        prepare_first_notification(user.uid)


def text_message_handle(bot, message):
    user = Botuser(message.chat.id)
    if message.text == db_connector.get_message_text_by_id(6):
        message_text = db_connector.get_message_text_by_id(1)
        keyboard = get_settings_keyboard()
        bot.send_message(user.uid, message_text, reply_markup=keyboard)
    elif message.text == db_connector.get_message_text_by_id(8):
        """ Добавить отправку результатов"""
        file_name = user.prepare_results()
        img = open(file_name, 'rb')
        bot.send_photo(user.uid, img, reply_to_message_id=message.message_id)


def update_settings(bot, call):
    user = Botuser(call.message.chat.id)
    data = call.data[4:]
    db_connector.update_notification_count(user.uid, data)
    message_text = db_connector.get_message_text_by_id(5)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)


def callback_handler(bot, call):
    user = Botuser(call.message.chat.id)
    data = call.data[9:]
    increment_answers(user=user, data=data)
    message_text = db_connector.get_message_text_by_id(5)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)