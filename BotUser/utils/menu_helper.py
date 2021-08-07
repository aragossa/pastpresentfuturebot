import datetime
import os
import time

from BotUser.utils.keyboard_helper import get_main_keyboard, get_request_keyboard
from utils import db_connector
from utils.db_connector import increment_answers, get_user_state, update_user_state, update_notification_count
from utils.logger import get_logger
from BotUser.bot_user import Botuser
from utils.notifications import Notification
from utils.scheduler import prepare_first_notification, prepare_next_notification

log = get_logger("menu_helper")


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


def check_user_state_input(uid):
    if get_user_state(uid=uid)[0] == "INPUT":
        return True


def add_user(bot, message):
    user = Botuser(message.chat.id)
    keyboard = get_main_keyboard()
    log.info(f"{user.check_auth()}")

    bot.send_message(user.uid, "test")

    if user.check_auth():
        message_text = db_connector.get_message_text_by_id(3)
        bot.send_message(user.uid, message_text, reply_markup=keyboard)

    else:
        if len(message.text.split()) > 1:
            log.info(f"found refer_id {message.text.split()[1]}")
            user.add_user(refer_id=message.text.split()[1])
        else:
            user.add_user()
        message_text = db_connector.get_message_text_by_id(3)
        bot.send_message(user.uid, message_text, reply_markup=keyboard)
        prepare_first_notification(user.uid)


def text_message_handle(bot, message):
    user = Botuser(message.chat.id)
    log.info(f"User state is {check_user_state_input(user.uid)}")
    # if check_user_state_input(user.uid):
    #     update_notification_count(user.uid, message.text)
    #     update_user_state(uid=user.uid, state="NULL", input_value="NULL")
    #     message_text = db_connector.get_message_text_by_id(10)
    #     bot.send_message(chat_id=user.uid, text=message_text, reply_to_message_id=message.message_id)
    #     log.info("STATE RESET")

    if message.text == db_connector.get_message_text_by_id(6):
        """ Меню настроки """

        message_text = db_connector.get_message_text_by_id(1)
        log.info("changing user state")
        update_user_state(uid=user.uid, state="INPUT", input_value="NULL")
        log.info("changed")
        bot.send_message(user.uid, message_text)
        # msg = bot.send_message(user.uid, message_text)
        # time.sleep(5)
        # bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="test")

    elif message.text == db_connector.get_message_text_by_id(8):
        """ Меню анализ """

        file_name = user.prepare_results()
        img = open(file_name, 'rb')
        bot.send_photo(user.uid, img, reply_to_message_id=message.message_id)
        os.remove(file_name)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(9):
        """ Меню оценить состояние """

        next_notification_state = "_skip"
        next_notification_id = int(db_connector.select_last_notification(user.uid)[0]) + 1
        keyboard = get_request_keyboard(next_notification_state, next_notification_id)
        message_text = db_connector.get_message_text_by_id(7)
        bot.send_message(chat_id=user.uid, text=message_text, reply_markup=keyboard)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")


    elif message.text == db_connector.get_message_text_by_id(11):
        """ Меню анализ в динамике """

        gif_file_name, file_names = user.prepare_results_dyn()

        img = open(gif_file_name, 'rb')
        bot.send_animation(user.uid, img, reply_to_message_id=message.message_id)

        os.remove(gif_file_name)
        for file_name in file_names:
            os.remove(file_name)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")


    elif message.text == db_connector.get_message_text_by_id(12):
        """ Меню поделиться """
        bot.send_message(user.uid, f"Ссылка для подключения к боту t.me/pronabudbot?start={user.uid}")
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(13):
        """ Меню мануал """

        message_text = db_connector.get_message_text_by_id(14)
        bot.send_message(user.uid, message_text)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")



    elif check_user_state_input(user.uid):
        log.info(f"message.text is int {is_int(message.text)}")
        if is_int(message.text):
            update_notification_count(user.uid, message.text)
            update_user_state(uid=user.uid, state="NULL", input_value="NULL")
            message_text = db_connector.get_message_text_by_id(10)
            bot.send_message(chat_id=user.uid, text=message_text, reply_to_message_id=message.message_id)
            log.info("STATE RESET")
        else:
            update_user_state(uid=user.uid, state="NULL", input_value="NULL")
            bot.send_message(chat_id=user.uid, text="Нужно указать целое число",
                             reply_to_message_id=message.message_id)
            log.info("STATE RESET")


def update_settings(bot, call):
    user = Botuser(call.message.chat.id)
    data = call.data[4:]
    db_connector.update_notification_count(user.uid, data)
    message_text = db_connector.get_message_text_by_id(5)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)


# SELECT COUNT("past_m") FROM results WHERE "creation_date" > "2021-06-08 15:00:00"
def callback_handler(bot, call):
    user = Botuser(call.message.chat.id)
    data = call.data.split("_")
    formatted_data = f"""{data[1]}_{data[2]}"""
    try:
        notification_id = data[4]
    except IndexError:
        notification_id = data[3]
    next_notification_state = True
    log.info(f"lenght of data - {len(data)}")
    if len(data) == 4:
        next_notification_state = False
    user.set_notification_complite(notification_id)
    log.info(f"next notification state - {next_notification_state}")
    creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.info(f"creation_date {creation_date}")
    increment_answers(user=user, data=formatted_data, creation_date=creation_date)
    message_text = db_connector.get_message_text_by_id(5)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)
    current = Notification(data_set=user.get_last_notification())
    if next_notification_state:
        prepare_next_notification(current)

def ref(bot, message):
    user = Botuser(message.chat.id)
