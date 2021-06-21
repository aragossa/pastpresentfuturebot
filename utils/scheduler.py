import time
import datetime

from BotUser.utils.keyboard_helper import get_request_keyboard
from utils import db_connector
from utils.db_connector import set_notification_sent, get_delay_hours, get_notification_count_by_uid, add_notification, \
    get_max_notification_id
from utils.logger import get_logger
from utils.notifications import Notification

# 8-9, 12-14, 18-21

log = get_logger("scheduler")

start_day = datetime.datetime.today().replace(hour=0, minute=00, second=00)
fin_day = datetime.datetime.today().replace(hour=23, minute=59, second=59)
period_1_start = datetime.datetime.today().replace(hour=8, minute=00, second=00)
period_1_finish = datetime.datetime.today().replace(hour=9, minute=00, second=00)
period_2_start = datetime.datetime.today().replace(hour=12, minute=00, second=00)
period_2_finish = datetime.datetime.today().replace(hour=14, minute=00, second=00)
period_3_start = datetime.datetime.today().replace(hour=18, minute=00, second=00)
period_3_finish = datetime.datetime.today().replace(hour=21, minute=00, second=00)


def check_period(check_datetime):
    log.info(check_datetime)
    status = "continue"
    log.info(status)
    log.info(start_day)
    log.info(fin_day)
    log.info(period_1_start)
    log.info(period_1_finish)
    log.info(period_2_start)
    log.info(period_2_finish)
    log.info(period_3_start)
    log.info(period_3_finish)

    if start_day <= check_datetime < period_1_start:
        log.info(f"""{period_1_start} {status}""")
        return period_1_start, status

    elif period_1_start <= check_datetime < period_1_finish:
        log.info(f"""{check_datetime} {status}""")
        return check_datetime, status

    elif period_1_finish <= check_datetime < period_2_start:
        log.info(f"""{period_2_start} {status}""")
        return period_2_start, status

    elif period_2_start <= check_datetime < period_2_finish:
        log.info(f"""{check_datetime} {status}""")
        return check_datetime, status

    elif period_2_finish <= check_datetime < period_3_start:
        log.info(f"""{period_3_start} {status}""")
        return period_3_start, status

    elif period_3_start <= check_datetime < period_3_finish:
        log.info(f"""{check_datetime} {status}""")
        return check_datetime, status

    else:
        status = "stop"
        log.info(f"""{period_3_finish} {status}""")
        return period_3_finish, status


def prepare_first_notification(uid):
    data_set = (get_max_notification_id, "REQUEST", uid, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "NEW", 1)
    print(data_set)
    current = Notification(data_set=data_set)
    log.info('preparing first notification')
    whole_time = int(get_delay_hours())
    notification_count = get_notification_count_by_uid(current.uid)
    hours_delta = int(whole_time / notification_count)
    log.info('Prepare today notification')
    this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
    next_datetime = this_datetime + datetime.timedelta(days=1)
    next_datetime_str = next_datetime.strftime('%Y-%m-%d')
    add_notification(current=current, next_datetime=f'{next_datetime_str} 09:00:00', step_id=current.step_id + 1)


def prepare_next_notification(current):
    log.info('preparing next notification')
    whole_time = int(get_delay_hours())
    notification_count = get_notification_count_by_uid(current.uid)
    hours_delta = int(whole_time / notification_count)
    if current.step_id <= notification_count - 1:
        log.info('Prepare today notification')
        next_datetime = datetime.datetime.now() + datetime.timedelta(hours=hours_delta)
        next_datetime_checked, status = check_period(next_datetime)

        next_datetime_str = next_datetime_checked.strftime('%Y-%m-%d %H:%M:%S')
        next_step = current.step_id + 1
        if status == "stop":
            next_datetime = datetime.datetime.today() + datetime.timedelta(days=1)
            next_datetime_str = f"""{next_datetime.strftime('%Y-%m-%d')} 08:00:00"""
            next_step = 1

        add_notification(current=current, next_datetime=next_datetime_str, step_id=next_step)

    elif current.step_id == notification_count:
        log.info('Prepare next day notification')
        this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
        next_datetime = this_datetime + datetime.timedelta(days=1)
        next_datetime_str = next_datetime.strftime('%Y-%m-%d')
        add_notification(current=current, next_datetime=f'{next_datetime_str} 08:00:00', step_id=1)


def check_pending(bot):
    while True:
        log.info('Prepare to sql query')
        for notification in db_connector.get_notifications():
            current = Notification(notification)
            log.info(f'Found notification id={current.id} for user {current.uid} with time {current.datetime}')
            if current.type == 'REQUEST':
                message_text = db_connector.get_message_text_by_id(7)
                log.info(f'Message for {current.uid} text = {message_text}')
                next_notification_state = ""
                keyboard = get_request_keyboard(next_notification_state)
                log.info('ready to send message')
                bot.send_message(chat_id=current.uid, text=message_text, reply_markup=keyboard)
                log.info('message sent')
                set_notification_sent(notification_id=current.id)
                # prepare_next_notification(current)
        log.info('Go to sleep 5 sec')
        time.sleep(5)
