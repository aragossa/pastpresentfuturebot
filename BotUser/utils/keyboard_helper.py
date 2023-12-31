from telebot import types

from utils import db_connector
from utils.logger import get_logger

log = get_logger("keyboardhelper")


def get_request_keyboard(next_notification_state, notification_id):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Прошлое', callback_data='empty')
    btn2 = types.InlineKeyboardButton(text='Настоящее', callback_data='empty')
    btn3 = types.InlineKeyboardButton(text='Будущее', callback_data='empty')
    btn4 = types.InlineKeyboardButton(text='+', callback_data=f'callback_past_p{next_notification_state}_{notification_id}')
    btn5 = types.InlineKeyboardButton(text='+', callback_data=f'callback_pres_p{next_notification_state}_{notification_id}')
    btn6 = types.InlineKeyboardButton(text='+', callback_data=f'callback_fut_p{next_notification_state}_{notification_id}')
    btn7 = types.InlineKeyboardButton(text='=', callback_data=f'callback_past_e{next_notification_state}_{notification_id}')
    btn8 = types.InlineKeyboardButton(text='=', callback_data=f'callback_pres_e{next_notification_state}_{notification_id}')
    btn9 = types.InlineKeyboardButton(text='=', callback_data=f'callback_fut_e{next_notification_state}_{notification_id}')
    btn10 = types.InlineKeyboardButton(text='-', callback_data=f'callback_past_m{next_notification_state}_{notification_id}')
    btn11 = types.InlineKeyboardButton(text='-', callback_data=f'callback_pres_m{next_notification_state}_{notification_id}')
    btn12 = types.InlineKeyboardButton(text='-', callback_data=f'callback_fut_m{next_notification_state}_{notification_id}')
    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12)
    return keyboard


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Настройки
    button_text_config = db_connector.get_message_text_by_id(6)
    btn1 = types.KeyboardButton(button_text_config)
    # Анализ
    button_text_analyse = db_connector.get_message_text_by_id(8)
    btn2 = types.KeyboardButton(button_text_analyse)
    # Оценить состояние
    button_text_analyse = db_connector.get_message_text_by_id(9)
    btn3 = types.KeyboardButton(button_text_analyse)
    # Анализ в динамике
    # button_text_analyse_dyn = db_connector.get_message_text_by_id(11)
    # btn4 = types.KeyboardButton(button_text_analyse_dyn)
    # Поделиться
    button_text_share = db_connector.get_message_text_by_id(12)
    btn5 = types.KeyboardButton(button_text_share)
    # Мануал
    button_text_manual = db_connector.get_message_text_by_id(13)
    btn6 = types.KeyboardButton(button_text_manual)
    # Объяснить
    # button_text_explain = db_connector.get_message_text_by_id(21)
    # btn7 = types.KeyboardButton(button_text_explain)

    keyboard.add(btn2, btn3)
    keyboard.add(btn6, btn5, btn1)
    return keyboard

def get_submenu_manual_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_text_user_state = db_connector.get_message_text_by_id(14)
    btn1 = types.KeyboardButton(button_text_user_state)
    button_text_button_descriprion = db_connector.get_message_text_by_id(18)
    btn2 = types.KeyboardButton(button_text_button_descriprion)
    button_text_explain = db_connector.get_message_text_by_id(21)
    btn3 = types.KeyboardButton(button_text_explain)
    keyboard.add(btn1, btn2, btn3)
    return keyboard

def get_submenu_analysis_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_text_analysis = db_connector.get_message_text_by_id(15)
    btn1 = types.KeyboardButton(button_text_analysis)
    button_text_dynamic_analysis = db_connector.get_message_text_by_id(16)
    btn2 = types.KeyboardButton(button_text_dynamic_analysis)
    keyboard.add(btn1, btn2)
    return keyboard

def get_survey_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='ДА', callback_data=f'surv_y')
    btn2 = types.InlineKeyboardButton(text='НЕТ', callback_data=f'surv_n')
    keyboard.add(btn1, btn2)
    return keyboard

def get_question_keyboard(uid, message_id):
    keyboard = types.InlineKeyboardMarkup()
    log.debug(f'reply_{uid}_{message_id}')
    btn1 = types.InlineKeyboardButton(text='Ответить', callback_data=f'reply_{uid}_{message_id}')
    keyboard.add(btn1)
    return keyboard


def get_feedback_keyboard(uid):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Позвонить', callback_data=f'feedback_call_{uid}')
    btn2 = types.InlineKeyboardButton(text='Заполнить форму', callback_data=f'feedback_form_{uid}')
    keyboard.add(btn1, btn2)
    return keyboard

def get_settings_submenu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    notify_count = db_connector.get_message_text_by_id(29)
    btn1 = types.KeyboardButton(notify_count)
    button_text_dynamic_analysis = db_connector.get_message_text_by_id(28)
    btn2 = types.KeyboardButton(button_text_dynamic_analysis)
    keyboard.add(btn1, btn2)
    return keyboard