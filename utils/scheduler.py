import time
import datetime

import telebot
from telebot.apihelper import ApiTelegramException

from BotUser.bot_user import Botuser
from BotUser.utils.keyboard_helper import get_request_keyboard
from BotUser.utils.send_message_timeout import send_message_timeout_five_times
from utils import db_connector
from utils.db_connector import set_notification_sent, get_delay_hours, get_notification_count_by_uid, add_notification, \
    get_max_notification_id, update_message_id, set_notification_blocked
from utils.logger import get_logger
from utils.notifications import Notification

# 8-9, 12-14, 18-21

log = get_logger("scheduler")

def get_today_limits():
    today = datetime.datetime.today()
    start_day = today.replace(hour=0, minute=00, second=00)
    fin_day = today.replace(hour=23, minute=59, second=59)
    # log.info(today.weekday())
    period_1_start = datetime.datetime.today().replace(hour=10, minute=00, second=00)
    period_1_finish = datetime.datetime.today().replace(hour=21, minute=00, second=00)
    log.info(f'get_today_limits start_day={start_day}, fin_day={fin_day}, period_1_start={period_1_start}, period_1_finish={period_1_finish}')
    return start_day, fin_day, period_1_start, period_1_finish


    # if today.weekday() == 6 or today.weekday() == 5:
    #
    #     period_1_start = datetime.datetime.today().replace(hour=10, minute=00, second=00)
    #     period_1_finish = datetime.datetime.today().replace(hour=19, minute=00, second=00)
    #     log.info(start_day)
    #     log.info(fin_day)
    #     log.info(period_1_start)
    #     log.info(period_1_finish)
    #     return start_day, fin_day, period_1_start, period_1_finish
    # else:
    #     period_1_start = datetime.datetime.today().replace(hour=8, minute=00, second=00)
    #     period_1_finish = datetime.datetime.today().replace(hour=9, minute=30, second=00)
    #     period_2_start = datetime.datetime.today().replace(hour=12, minute=30, second=00)
    #     period_2_finish = datetime.datetime.today().replace(hour=14, minute=00, second=00)
    #     period_3_start = datetime.datetime.today().replace(hour=19, minute=00, second=00)
    #     period_3_finish = datetime.datetime.today().replace(hour=22, minute=00, second=00)
    #     return start_day, fin_day, period_1_start, period_1_finish, period_2_start, period_2_finish, period_3_start, period_3_finish


def get_sum(datetime_start, datetime_finish):
    return (datetime_finish - datetime_start).seconds // 60


def minutes_left_to_send():
    now = datetime.datetime.now()

    start_day, fin_day, period_1_start, period_1_finish = get_today_limits()
    if start_day <= now < period_1_start:
        minutes_left = get_sum(now, period_1_finish)
        return minutes_left

    elif period_1_start <= now < period_1_finish:
        minutes_left = get_sum(now, period_1_finish)
        return minutes_left

    else:
        return 0

    # if now.weekday() == 6 or now.weekday() == 5:
    #     start_day, fin_day, period_1_start, period_1_finish = get_today_limits()
    #     if start_day <= now < period_1_start:
    #         minutes_left = get_sum(now, period_1_finish)
    #         return minutes_left
    #
    #     elif period_1_start <= now < period_1_finish:
    #         minutes_left = get_sum(now, period_1_finish)
    #         return minutes_left
    #
    #     else:
    #         return 0
    #
    # else:
    #     start_day, fin_day, period_1_start, period_1_finish, period_2_start, period_2_finish, period_3_start, period_3_finish = get_today_limits()
    #     if start_day <= now < period_1_start:
    #         minutes_left = get_sum(now, period_3_finish)
    #         return minutes_left
    #
    #     elif period_1_start <= now < period_1_finish:
    #         minutes_left = get_sum(now, period_1_finish) + get_sum(period_2_start, period_2_finish) + get_sum(
    #             period_3_start, period_3_finish)
    #         return minutes_left
    #
    #     elif period_1_finish <= now < period_2_start:
    #         minutes_left = get_sum(period_2_start, period_2_finish) + get_sum(
    #             period_3_start, period_3_finish)
    #         return minutes_left
    #
    #     elif period_2_start <= now < period_2_finish:
    #         minutes_left = get_sum(now, period_2_finish) + get_sum(
    #             period_3_start, period_3_finish)
    #         return minutes_left
    #
    #     elif period_2_finish <= now < period_3_start:
    #         minutes_left = get_sum(period_3_start, period_3_finish)
    #         return minutes_left
    #
    #     elif period_3_start <= now < period_3_finish:
    #         minutes_left = get_sum(now, period_3_finish)
    #         return minutes_left
    #
    #     else:
    #         return 0


def check_period(check_datetime):
    now = datetime.datetime.now()
    start_day, fin_day, period_1_start, period_1_finish = get_today_limits()
    status = "continue"
    log.info(status)

    if start_day <= check_datetime < period_1_start:
        log.info(f"""Next period is {period_1_start} {status}""")
        return period_1_start, status

    elif period_1_start <= check_datetime < period_1_finish:
        log.info(f"""Next period is {check_datetime} {status}""")
        return check_datetime, status

    else:
        return 0

    # if now.weekday() == 6 or now.weekday() == 5:
    #     start_day, fin_day, period_1_start, period_1_finish = get_today_limits()
    #     status = "continue"
    #     log.info(status)
    #
    #     if start_day <= check_datetime < period_1_start:
    #         log.info(f"""Next period is {period_1_start} {status}""")
    #         return period_1_start, status
    #
    #     elif period_1_start <= check_datetime < period_1_finish:
    #         log.info(f"""Next period is {check_datetime} {status}""")
    #         return check_datetime, status
    #
    #     else:
    #         return 0


    # else:
    #     start_day, fin_day, period_1_start, period_1_finish, period_2_start, period_2_finish, period_3_start, period_3_finish = get_today_limits()
    #     log.info(check_datetime)
    #     status = "continue"
    #     log.info(status)
    #
    #     if start_day <= check_datetime < period_1_start:
    #         log.info(f"""Next period is {period_1_start} {status}""")
    #         return period_1_start, status
    #
    #     elif period_1_start <= check_datetime < period_1_finish:
    #         log.info(f"""Next period is {check_datetime} {status}""")
    #         return check_datetime, status
    #
    #     elif period_1_finish <= check_datetime < period_2_start:
    #         log.info(f"""Next period is {period_2_start} {status}""")
    #         return period_2_start, status
    #
    #     elif period_2_start <= check_datetime < period_2_finish:
    #         log.info(f"""Next period is {check_datetime} {status}""")
    #         return check_datetime, status
    #
    #     elif period_2_finish <= check_datetime < period_3_start:
    #         log.info(f"""Next period is {period_3_start} {status}""")
    #         return period_3_start, status
    #
    #     elif period_3_start <= check_datetime < period_3_finish:
    #         log.info(f"""Next period is {check_datetime} {status}""")
    #         return check_datetime, status
    #
    #     elif period_3_finish <= check_datetime <= fin_day:
    #         status = "stop"
    #         log.info(f"""Next period is {period_3_finish} {status}""")
    #         return period_3_finish, status


def prepare_first_notification(uid):
    data_set = (
    get_max_notification_id, "REQUEST", uid, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "NEW", 1)
    print(data_set)
    current = Notification(data_set=data_set)
    log.info('preparing first notification')
    # whole_time = int(get_delay_hours())
    # notification_count = get_notification_count_by_uid(current.uid)
    # hours_delta = int(whole_time / notification_count)
    log.info('Prepare today notification')
    this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
    next_datetime = this_datetime + datetime.timedelta(days=1)
    next_datetime_str = next_datetime.strftime('%Y-%m-%d')
    log.info(f"current.step_id {current.step_id}")
    add_notification(current=current, next_datetime=f'{next_datetime_str} 08:00:00', step_id=current.step_id + 1)


def prepare_next_notification(current):
    log.info('preparing next notification')
    # whole_time = int(get_delay_hours())
    whole_time_left = minutes_left_to_send()
    notification_count = get_notification_count_by_uid(current.uid)
    try:
        minutes_left_delta = int(whole_time_left / notification_count)
    except ZeroDivisionError:
        minutes_left_delta = 0
    log.info(f"notification_count:{notification_count}, minutes_delta:{minutes_left_delta}, whole_time: {whole_time_left}")
    log.info(f"current {current.step_id}")
    if (current.step_id <= notification_count - 1) and minutes_left_delta >= 20:
        log.info('Prepare today notification')
        next_datetime = (datetime.datetime.now() + datetime.timedelta(minutes=minutes_left_delta))
        log.info(f"next_datetime {next_datetime}")
        next_datetime_checked, status = check_period(next_datetime)

        next_datetime_str = next_datetime_checked.strftime('%Y-%m-%d %H:%M:%S')
        log.info(f"next_datetime_str {next_datetime_str}")
        next_step = current.step_id + 1
        if status == "stop":
            next_datetime = datetime.datetime.today() + datetime.timedelta(days=1)
            next_datetime_str = f"""{next_datetime.strftime('%Y-%m-%d')} 08:00:00"""
            next_step = 1

        add_notification(current=current, next_datetime=next_datetime_str, step_id=next_step)

    else:
        log.info('Prepare next day notification')
        this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
        next_datetime = this_datetime + datetime.timedelta(days=1)
        next_datetime_str = next_datetime.strftime('%Y-%m-%d')
        add_notification(current=current, next_datetime=f'{next_datetime_str} 08:00:00', step_id=1)


def check_pending(bot):
    while True:
        #log.info('Prepare to sql query')
        for notification in db_connector.get_notifications():
            current = Notification(notification)
            log.info(f'Found notification id={current.id} for user {current.uid} with time {current.datetime}')
            if current.type == 'REQUEST':
                prev_status, prev_message_id = Botuser.get_last_notification_status(current.uid)
                log.info(f"prev_status {prev_status}")
                log.info(f"prev_message_id {prev_message_id}")
                message_text = db_connector.get_message_text_by_id(7)
                #log.info(f'Message for {current.uid} text = {message_text}')
                next_notification_state = ""
                keyboard = get_request_keyboard(next_notification_state, current.id)
                log.info('ready to send message')
                try:

                    msg = send_message_timeout_five_times(bot, current.uid, message_text, keyboard)
                    #log.info(msg)
                    log.info('message sent')
                    set_notification_sent(notification_id=current.id)
                    update_message_id(notification_id=current.id, message_id=msg.message_id)
                    if prev_status != 'COMPLITE' and prev_message_id is not None:
                        log.info(f"{current.uid}, {prev_message_id}")
                        try:
                            bot.delete_message(chat_id=current.uid, message_id=prev_message_id)
                        except ApiTelegramException:
                            pass
                    prepare_next_notification(current)
                    time.sleep(5)
                except telebot.apihelper.ApiTelegramException as e:
                    log.exception(e)
                    log.info(f'user {current.uid} blocked')
                    set_notification_blocked(notification_id=current.id)


        #log.info('Go to sleep 5 sec')
        time.sleep(5)
