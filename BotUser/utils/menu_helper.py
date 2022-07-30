import datetime
import os
import time

from BotUser.utils.get_stats import UserStats
from BotUser.utils.keyboard_helper import get_main_keyboard, get_request_keyboard, get_submenu_manual_keyboard, \
    get_submenu_analysis_keyboard, get_survey_keyboard, get_question_keyboard
from BotUser.utils.send_message_timeout import send_message_timeout_five_times
from utils import db_connector
from utils.db_connector import increment_answers, get_user_state, update_user_state, update_notification_count, \
    add_notification
from utils.logger import get_logger
from BotUser.bot_user import Botuser
from utils.notifications import Notification
from utils.scheduler import prepare_first_notification

log = get_logger("menu_helper")


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def add_feedback_notification(user):
    data_set = (
        1, "FEEDBACK", user.uid, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "NEW", 1)

    current = Notification(data_set=data_set)
    this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
    next_datetime = this_datetime + datetime.timedelta(days=21)
    next_datetime_str = next_datetime.strftime('%Y-%m-%d')
    add_notification(current=current, next_datetime=f'{next_datetime_str} 12:00:00', step_id=current.step_id + 1)


def admin_notify(bot, user):
    time.sleep(1)
    new_user_notification = f"""Подключился новый пользователь:
    id: {user.uid},
    username: {user.username},
    first_name: {user.first_name},
    last_name: {user.last_name}"""
    send_message_timeout_five_times(bot, 121013858, new_user_notification)
    time.sleep(1)


def refer_notify(bot, refer_id):
    time.sleep(1)
    message_text = db_connector.get_message_text_by_id(24)
    send_message_timeout_five_times(bot, refer_id, message_text)


def check_user_state_input(uid):
    if get_user_state(uid=uid)[0] == "INPUT":
        return "INPUT"
    elif get_user_state(uid=uid)[0] == "INPUT_QUESTION":
        return "INPUT_QUESTION"
    elif get_user_state(uid=uid)[0] == "REPLY_TO":
        return "REPLY_TO"
    elif get_user_state(uid=uid)[0] == 'FEEDBACK_PHONE':
        return 'FEEDBACK_PHONE'
    elif get_user_state(uid=uid)[0] == 'FEEDBACK_TIME':
        return 'FEEDBACK_TIME'



def add_user(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    keyboard = get_main_keyboard()
    log.info(f"{user.check_auth()}")

    if user.check_auth():
        message_text = db_connector.get_message_text_by_id(3)
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)

    else:
        if len(message.text.split()) > 1:
            refer_id = message.text.split()[1]
            if db_connector.check_refer_id(refer_id):
                log.info(f"found refer_id {refer_id}")
                user.add_user(refer_id=refer_id)
                refer_notify(bot=bot, refer_id=refer_id)
            else:
                log.info(f"failed to find refer_id {refer_id}")
        else:
            user.add_user()
        message_text = db_connector.get_message_text_by_id(3)
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)

        admin_notify(bot=bot, user=user)
        prepare_first_notification(user.uid)
        add_feedback_notification(user=user)


def text_message_handle(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    log.info(f"User state is {check_user_state_input(user.uid)}")

    if message.text == db_connector.get_message_text_by_id(6):
        """ Меню настроки """

        message_text = db_connector.get_message_text_by_id(1)
        log.info("changing user state")
        update_user_state(uid=user.uid, state="INPUT", input_value="NULL")
        log.info("changed")
        send_message_timeout_five_times(bot, user.uid, message_text)

    elif message.text == db_connector.get_message_text_by_id(9):
        """ Меню оценить состояние """

        next_notification_state = "_skip"
        next_notification_id = int(db_connector.select_last_notification(user.uid)[0]) + 1
        keyboard = get_request_keyboard(next_notification_state, next_notification_id)
        message_text = db_connector.get_message_text_by_id(7)
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(12):
        """ Меню поделиться """
        send_message_timeout_five_times(bot, user.uid,
                                        f"Ссылка для подключения к боту t.me/pronabudbot?start={user.uid}")
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(13):
        """ Меню мануал """
        keyboard = get_submenu_manual_keyboard()
        message_text = db_connector.get_message_text_by_id(13)
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(8):
        """ Меню анализ """
        keyboard = get_submenu_analysis_keyboard()
        message_text = db_connector.get_message_text_by_id(8)
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(21):
        """ Поденю Концепции """
        keyboard = get_main_keyboard()
        message_text = db_connector.get_message_text_by_id(22)
        send_message_timeout_five_times(bot, user.uid, message_text, parse_mode='markdown', reply_markup=keyboard)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(14):
        """ Подменю Вопрос автору """
        keyboard = get_main_keyboard()
        message_text = db_connector.get_message_text_by_id(17)
        update_user_state(uid=user.uid, state="INPUT_QUESTION", input_value="NULL")
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(18):
        """ Подменю Описание кнопок """
        keyboard = get_main_keyboard()
        message_text = db_connector.get_message_text_by_id(20)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        send_message_timeout_five_times(bot, user.uid, message_text, reply_markup=keyboard)
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(15):
        """ Подменю анализ """
        keyboard = get_main_keyboard()
        file_name = user.prepare_results()
        img = open(file_name, 'rb')
        bot.send_photo(user.uid, img, reply_to_message_id=message.message_id)
        os.remove(file_name)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        send_message_timeout_five_times(bot, user.uid, "меню", reply_markup=keyboard)
        log.info("STATE RESET")

    elif message.text == db_connector.get_message_text_by_id(16):
        """ Подменю анализ в динамике """
        keyboard = get_main_keyboard()
        gif_file_name, file_names = user.prepare_results_dyn()

        img = open(gif_file_name, 'rb')
        bot.send_animation(user.uid, img, reply_to_message_id=message.message_id)

        os.remove(gif_file_name)
        for file_name in file_names:
            os.remove(file_name)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        send_message_timeout_five_times(bot, user.uid, "меню", reply_markup=keyboard)
        log.info("STATE RESET")

    elif check_user_state_input(user.uid) == "INPUT":
        """ Обработка количества уведомлений пользователю """
        log.info(f"message.text is int {is_int(message.text)}")
        if is_int(message.text):
            update_notification_count(user.uid, message.text)
            update_user_state(uid=user.uid, state="NULL", input_value="NULL")
            message_text = db_connector.get_message_text_by_id(10)
            send_message_timeout_five_times(bot, user.uid, message_text, reply_to_message_id=message.message_id)
            log.info("STATE RESET")
        else:
            update_user_state(uid=user.uid, state="NULL", input_value="NULL")
            send_message_timeout_five_times(bot, user.uid, "Нужно указать целое число",
                                            reply_to_message_id=message.message_id)
            log.info("STATE RESET")

    elif check_user_state_input(user.uid) == "INPUT_QUESTION":
        """ Обработка вопроса автору """
        keyboard = get_question_keyboard(uid=user.uid, message_id=message.id)
        send_message_timeout_five_times(bot, user.uid, "Ваш вопрос отправлен",
                                        reply_to_message_id=message.message_id)
        prepared_message_text = f"""Вопрос от пользователя {user.username} ({user.first_name} {user.last_name}):
{message.text}"""
        send_message_timeout_five_times(bot, 556047985, prepared_message_text, reply_markup=keyboard)
        send_message_timeout_five_times(bot, 121013858, prepared_message_text, reply_markup=keyboard)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

    elif check_user_state_input(user.uid) == "REPLY_TO":
        log.debug(get_user_state(uid=user.uid))
        formatted_data = get_user_state(uid=user.uid)[1]
        log.debug(formatted_data)
        recipient_uid = formatted_data.split('_')[0]
        recipient_message_id = formatted_data.split('_')[1]
        prepared_message_text = f"""Саша Зеленин:\n{message.text}"""
        send_message_timeout_five_times(bot, recipient_uid, prepared_message_text,
                                        reply_to_message_id=recipient_message_id)
    elif check_user_state_input(user.uid) == 'FEEDBACK_PHONE':
        message_text = db_connector.get_message_text_by_id(28)
        send_message_timeout_five_times(bot, message.chat.id, message_text)
        update_user_state(uid=message.chat.id, state="FEEDBACK_TIME", input_value=message.text)

    elif check_user_state_input(user.uid) == 'FEEDBACK_TIME':
        send_message_timeout_five_times(bot, message.chat.id, 'Спасибо!')
        input_value = get_user_state(uid=user.uid)[1]
        admin_message_text = f"Фидбэк от пользователя {message.chat.id}: {input_value}, {message.text}"
        send_message_timeout_five_times(bot, 556047985, admin_message_text)
        send_message_timeout_five_times(bot, 121013858, admin_message_text)
        update_user_state(uid=user.uid, state="NULL", input_value="NULL")
        log.info("STATE RESET")

def update_settings(bot, call):
    user = Botuser(uid=call.message.chat.id,
                   username=call.message.chat.username,
                   first_name=call.message.chat.first_name,
                   last_name=call.message.chat.last_name)
    data = call.data[4:]
    db_connector.update_notification_count(user.uid, data)
    message_text = db_connector.get_message_text_by_id(5)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)


# SELECT COUNT("past_m") FROM results WHERE "creation_date" > "2021-06-08 15:00:00"
def callback_handler(bot, call):
    user = Botuser(uid=call.message.chat.id,
                   username=call.message.chat.username,
                   first_name=call.message.chat.first_name,
                   last_name=call.message.chat.last_name)
    log.info(call.data)
    data = call.data.split("_")
    formatted_data = f"""{data[1]}_{data[2]}"""

    try:
        notification_id = data[4]
    except IndexError:
        notification_id = data[3]
    next_notification_state = True
    log.info(f"lenght of data - {len(data)}")
    log.info(f"formatted_data {formatted_data}")
    if len(data) == 5:

        next_notification_state = False
    else:
        user.set_notification_complite(notification_id)
    creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if next_notification_state:
        scheduled_time = db_connector.get_notification_scheduled_time(notification_id)
        scheduled_time_formatted = datetime.datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M:%S')
        log.info(f"next notification state - {next_notification_state}")

        log.info(f"creation_date {creation_date}")
        response_time = int((datetime.datetime.now() - scheduled_time_formatted).total_seconds() / 60.0)
        increment_answers(user=user, data=formatted_data, creation_date=creation_date, response_time=response_time)
    else:
        increment_answers(user=user, data=formatted_data, creation_date=creation_date)
    message_text = db_connector.get_message_text_by_id(5)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)
    # current = Notification(data_set=user.get_last_notification())
    # if next_notification_state:
    #     prepare_next_notification(current)


def survey_results(bot, call):
    log.info(f"Survey results {call.message.chat.id} - {call.data}")
    message_text = 'Спасибо за участие'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)


def prepare_survey(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    keyboard = get_survey_keyboard()
    text = """
Привет, это Саша. 
Бот упал, сорян😬, уже чиним».

Если найдёшь время, ответь пожалуйста, были какие-то инсайты после использования бота или нет. Другими словами, получил ты какую-то пользу или нет?
Ответ мне нужен, чтобы не улетать в илюзии и принимать решения о развитие проекта на основании фидбэка, а не ожиданий."""
    users = user.get_bot_active_users()
    for curr_user in users:
        log.info(f'sending survey to user {user}')
        send_message_timeout_five_times(bot, curr_user, text, reply_markup=keyboard)
        time.sleep(5)


def send_text(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    users = user.get_bot_active_users()
    text = message.text.replace('/adminadminsendmessageadminadmin', '')
    log.debug(text)
    log.debug(users)
    for curr_user in users:
        log.info(f'sending text to user {user}')
        send_message_timeout_five_times(bot, curr_user, text, parse_mode='Markdown')
        time.sleep(5)


def update_user_menu(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    users = user.get_bot_active_users()
    message_text = 'Привет! Мы обновили меню, появилась кнопка'
    keyboard = get_main_keyboard()
    for curr_user in users:
        log.info(f'sending text to user {user} to update menu')
        send_message_timeout_five_times(bot, curr_user, message_text, reply_markup=keyboard)
        time.sleep(5)


def get_stats(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    if user.uid in [121013858, 556047985]:
        stats = UserStats()
        get_bot_users_stats = stats.get_stats()
        blocked = stats.get_blocked_users()
        yesterday_users = stats.get_yestarday_users()
        top_refers = stats.top_refers()
        send_message_timeout_five_times(bot, message.chat.id, blocked)
        send_message_timeout_five_times(bot, message.chat.id, yesterday_users)
        send_message_timeout_five_times(bot, message.chat.id, get_bot_users_stats)
        send_message_timeout_five_times(bot, message.chat.id, top_refers)

    else:
        send_message_timeout_five_times(bot, message.chat.id, 'У Вас нет прав админа')


def get_users_stat(bot, message):
    user = Botuser(uid=message.chat.id,
                   username=message.chat.username,
                   first_name=message.chat.first_name,
                   last_name=message.chat.last_name)
    if user.uid in [121013858, 556047985]:
        users_info = db_connector.get_bot_users()
        for curr_user in users_info:
            log.debug(curr_user)

            last_notification = db_connector.select_last_notification(curr_user[0])
            message_text = f"""Информация о пользователе:
    id:{curr_user[0]}, username:{curr_user[1]},  first_name:{curr_user[2]}, last_name:{curr_user[3]}
    Дата подключения: {curr_user[4]}
    Последнее использование: {last_notification[3]}"""
            if last_notification[4] == 'BLOCKED':
                message_text += """\nПользователь заблокировал бота"""
            log.debug(last_notification)
            time.sleep(1)
            send_message_timeout_five_times(bot, user.uid, message_text)

    else:
        send_message_timeout_five_times(bot, message.chat.id, 'У Вас нет прав админа')


def question_reply(bot, call):
    data = call.data.split("_")
    log.debug(call)
    formatted_data = f"""{data[1]}_{data[2]}"""
    update_user_state(uid=call.message.chat.id, state="REPLY_TO", input_value=formatted_data)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
    send_message_timeout_five_times(bot, call.message.chat.id, "Введите ответ:")


def feedback_reply(bot, call):
    data = call.data.split("_")
    formatted_data = f"""{data[1]}_{data[2]}"""
    feedback_choice = data[1]
    feedback_user = data[2]
    log.info(feedback_choice)
    if feedback_choice == 'form':
        message_text = db_connector.get_message_text_by_id(25)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text)

    else:
        message_text = db_connector.get_message_text_by_id(26)
        send_message_timeout_five_times(bot, call.message.chat.id, message_text)
        update_user_state(uid=call.message.chat.id, state="FEEDBACK_PHONE", input_value=formatted_data)
