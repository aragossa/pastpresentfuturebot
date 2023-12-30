import time
import telebot
import requests


def send_message_timeout_five_times(bot, uid, message_text, reply_markup=None, reply_to_message_id=None, parse_mode=None):
    for i in range(5):
        try:
            return bot.send_message(uid, message_text, reply_markup=reply_markup, reply_to_message_id=reply_to_message_id, parse_mode=parse_mode)
        except requests.exceptions.ConnectionError:
            time.sleep(5)
        except telebot.apihelper.ApiTelegramException:
            return None