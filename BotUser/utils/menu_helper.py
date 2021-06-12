import os

from BotUser.utils.keyboard_helper import get_main_keyboard, get_settings_keyboard, get_request_keyboard
from utils import db_connector
from utils.db_connector import increment_answers, get_user_state, update_user_state, update_notification_count
from utils.logger import get_logger
from BotUser.bot_user import Botuser
from utils.notifications import Notification
from utils.scheduler import prepare_first_notification, prepare_next_notification

log = get_logger("menu_helper")


def check_user_state_input(uid):
    if get_user_state(uid=uid)[0] == "INPUT":
        return True


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
    log.info(f"User state is {check_user_state_input(user.uid)}")
    if check_user_state_input(user.uid):
        update_notification_count(user.uid, message.text)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        message_text = db_connector.get_message_text_by_id(10)
        bot.send_message(chat_id=user.uid, text=message_text, reply_to_message_id=message.message_id)
        log.info("STATE RESET")

    else:
        if message.text == db_connector.get_message_text_by_id(6):
            message_text = db_connector.get_message_text_by_id(1)
            log.info("changing user state")
            update_user_state(uid=user.uid, state="INPUT", input_value="NULL")
            log.info("changed")
            bot.send_message(user.uid, message_text)
        elif message.text == db_connector.get_message_text_by_id(8):
            file_name = user.prepare_results()
            img = open(file_name, 'rb')
            bot.send_photo(user.uid, img, reply_to_message_id=message.message_id)
            os.remove(file_name)
        elif message.text == db_connector.get_message_text_by_id(9):
            keyboard = get_request_keyboard()
            message_text = db_connector.get_message_text_by_id(7)
            bot.send_message(chat_id=user.uid, text=message_text, reply_markup=keyboard)


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
    current = Notification(data_set=user.get_last_notification())
    prepare_next_notification(current)