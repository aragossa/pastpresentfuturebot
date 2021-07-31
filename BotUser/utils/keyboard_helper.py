from telebot import types

from utils import db_connector
from utils.logger import get_logger

log = get_logger("keyboardhelper")


def get_request_keyboard(next_notification_state):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Прошлое', callback_data='empty')
    btn2 = types.InlineKeyboardButton(text='Настоящее', callback_data='empty')
    btn3 = types.InlineKeyboardButton(text='Будущее', callback_data='empty')
    btn4 = types.InlineKeyboardButton(text='+', callback_data=f'callback_past_p{next_notification_state}')
    btn5 = types.InlineKeyboardButton(text='+', callback_data=f'callback_pres_p{next_notification_state}')
    btn6 = types.InlineKeyboardButton(text='+', callback_data=f'callback_fut_p{next_notification_state}')
    btn7 = types.InlineKeyboardButton(text='=', callback_data=f'callback_past_e{next_notification_state}')
    btn8 = types.InlineKeyboardButton(text='=', callback_data=f'callback_pres_e{next_notification_state}')
    btn9 = types.InlineKeyboardButton(text='=', callback_data=f'callback_fut_e{next_notification_state}')
    btn10 = types.InlineKeyboardButton(text='-', callback_data=f'callback_past_m{next_notification_state}')
    btn11 = types.InlineKeyboardButton(text='-', callback_data=f'callback_pres_m{next_notification_state}')
    btn12 = types.InlineKeyboardButton(text='-', callback_data=f'callback_fut_m{next_notification_state}')
    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12)
    return keyboard


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_text_config = db_connector.get_message_text_by_id(6)
    btn1 = types.KeyboardButton(button_text_config)
    button_text_analyse = db_connector.get_message_text_by_id(8)
    btn2 = types.KeyboardButton(button_text_analyse)
    button_text_analyse = db_connector.get_message_text_by_id(9)
    btn3 = types.KeyboardButton(button_text_analyse)
    button_text_analyse_dyn = db_connector.get_message_text_by_id(11)
    btn4 = types.KeyboardButton(button_text_analyse_dyn)
    button_text_share = db_connector.get_message_text_by_id(12)
    btn5 = types.KeyboardButton(button_text_share)
    button_text_manual = db_connector.get_message_text_by_id(13)
    btn6 = types.KeyboardButton(button_text_manual)

    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return keyboard


def get_settings_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='1', callback_data='set_1')
    btn2 = types.InlineKeyboardButton(text='2', callback_data='set_2')
    btn3 = types.InlineKeyboardButton(text='3', callback_data='set_3')
    btn4 = types.InlineKeyboardButton(text='4', callback_data='set_4')
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard
