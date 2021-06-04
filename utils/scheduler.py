import time
import datetime

from BotUser.utils.keyboard_helper import get_request_keyboard
from utils import db_connector
from utils.db_connector import set_notification_sent, get_delay_hours, get_notification_count_by_uid, add_notification
from utils.logger import get_logger
from utils.notifications import Notification

log = get_logger("scheduler")

def prepare_next_notification(current):
    log.info('preparing next notification')
    whole_time = int(get_delay_hours())
    notification_count = get_notification_count_by_uid(current.uid)
    hours_delta = int(whole_time/notification_count)
    if current.step_id <= notification_count - 1:
        log.info('Prepare today notification')
        this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
        next_datetime = this_datetime + datetime.timedelta(hours=hours_delta)
        next_datetime_str = next_datetime.strftime('%Y-%m-%d %H:%M:%S')
        add_notification(current=current, next_datetime=next_datetime_str, step_id=current.step_id + 1)
    elif current.step_id == notification_count:
        log.info('Prepare next day notification')
        this_datetime = datetime.datetime.strptime(current.datetime, '%Y-%m-%d %H:%M:%S')
        next_datetime = this_datetime + datetime.timedelta(days=1)
        next_datetime_str = next_datetime.strftime('%Y-%m-%d')
        add_notification(current=current, next_datetime=f'{next_datetime_str} 09:00:00', step_id=1)



def check_pending(bot):
    while True:
        log.info('Prepare to sql query')
        for notification in db_connector.get_notifications():
            current = Notification(notification)
            log.info(f'Found notification id={current.id} for user {current.uid} with time {current.datetime}')
            if current.type == 'REQUEST':
                message_text = db_connector.get_message_text_by_id(7)
                log.info(f'Message for {current.uid} text = {message_text}')
                keyboard = get_request_keyboard()
                log.info('ready to send message')
                bot.send_message(chat_id=current.uid, text=message_text, reply_markup=keyboard)
                log.info('message sent')
                set_notification_sent(notification_id=current.id)
                prepare_next_notification(current)
        log.info('Go to sleep 5 sec')
        time.sleep(5)


