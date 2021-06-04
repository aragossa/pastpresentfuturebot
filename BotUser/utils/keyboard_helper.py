from telebot import types

from utils import db_connector
from utils.logger import get_logger

log = get_logger("keyboardhelper")


def get_request_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Прошлое', callback_data='empty')
    btn2 = types.InlineKeyboardButton(text='Настоящее', callback_data='empty')
    btn3 = types.InlineKeyboardButton(text='Будущее', callback_data='empty')
    btn4 = types.InlineKeyboardButton(text='+', callback_data='callback_past_p')
    btn5 = types.InlineKeyboardButton(text='+', callback_data='callback_pres_p')
    btn6 = types.InlineKeyboardButton(text='+', callback_data='callback_fut_p')
    btn7 = types.InlineKeyboardButton(text='=', callback_data='callback_past_e')
    btn8 = types.InlineKeyboardButton(text='=', callback_data='callback_pres_e')
    btn9 = types.InlineKeyboardButton(text='=', callback_data='callback_fut_e')
    btn10 = types.InlineKeyboardButton(text='-', callback_data='callback_past_m')
    btn11 = types.InlineKeyboardButton(text='-', callback_data='callback_pres_m')
    btn12 = types.InlineKeyboardButton(text='-', callback_data='callback_fut_m')
    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12)
    return keyboard


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    message_text = db_connector.get_message_text_by_id(6)
    btn = types.KeyboardButton(message_text)
    keyboard.add(btn)
    return keyboard


def get_settings_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='1', callback_data='set_1')
    btn2 = types.InlineKeyboardButton(text='2', callback_data='set_2')
    btn3 = types.InlineKeyboardButton(text='3', callback_data='set_3')
    btn4 = types.InlineKeyboardButton(text='4', callback_data='set_4')
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard
