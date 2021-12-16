import telebot
from multiprocessing import Process

from BotUser.utils import menu_helper
from BotUser.utils.menu_helper import callback_handler
from utils.db_connector import get_api_token, connection
from utils.logger import get_logger
from utils.scheduler import check_pending

log = get_logger("main handler")
TOKEN = get_api_token()
bot = telebot.TeleBot(TOKEN)


"t.me/Madbetbot?start=3f4f2bd6-fdf5-49d3-9a0c-1b3d630d7de2"

@bot.message_handler(commands=['start'])
def command_start_handler(m):
    try:
        menu_helper.add_user(bot=bot, message=m)
    except Exception as e:
        log.exception(e)
        log.exception(m)
        bot.send_message(m.chat.id, 'Что-то пошло не так')

@bot.message_handler(commands=['adminadminsendsurveyadminadmin'])
def set_username(m):
    try:
        menu_helper.prepare_survey(bot=bot, message=m)
    except:
        log.exception(m)
        log.exception('Got exception on main handler')
        bot.send_message(m.chat.id,
                         'Имя пользователя не указано. Используйте команду\n\n/setusername Ваше_Имя_Пользователя ')

@bot.message_handler(content_types='text')
def simple_text_message(m):
    try:
        menu_helper.text_message_handle(bot=bot, message=m)
    except Exception as e:
        log.exception(e)
        log.exception(m)
        bot.send_message(m.chat.id, 'Что-то пошло не так')


@bot.callback_query_handler(func=lambda call: call.data[:9] == 'callback_')
def request_state_handler(call):
    try:
        callback_handler(bot=bot, call=call)
    except Exception as e:
        log.exception(e)
        log.exception(call)
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')


@bot.callback_query_handler(func=lambda call: call.data[:4] == 'set_')
def settings_handler(call):
    try:
        menu_helper.update_settings(bot=bot, call=call)
    except Exception as e:
        log.exception(e)
        log.exception(call)
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')

@bot.callback_query_handler(func=lambda call: call.data[:5] == 'surv_')
def vote_request(call):
    try:
        menu_helper.survey_results(bot=bot, call=call)
    except:
        log.exception(call)
        log.exception('Got exception on main handler')
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')


if __name__ == '__main__':
    p1 = Process(target=check_pending, args=(bot,))
    p1.start()
    print('Listerning...')
    bot.polling(none_stop=True)
