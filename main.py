import telebot
from multiprocessing import Process
import ssl
from aiohttp import web

from BotUser.utils import menu_helper
from BotUser.utils.menu_helper import callback_handler
from utils.db_connector import get_api_token
from utils.logger import get_logger
from utils.scheduler import check_pending

log = get_logger("main handler")
TOKEN = get_api_token()

WEBHOOK_HOST = '185.159.129.94'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '185.159.129.94'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem' # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)

bot = telebot.TeleBot(TOKEN)
log.debug(TOKEN)

app = web.Application()



# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)

@bot.message_handler(commands=['start'])
def command_start_handler(m):
    try:
        menu_helper.add_user(bot=bot, message=m)
    except Exception as e:
        log.exception(e)
        log.exception(m)
        bot.send_message(m.chat.id, 'Что-то пошло не так')

@bot.message_handler(commands=['adminadminsendsurveyadminadmin'])
def send_survey(m):
    try:
        menu_helper.prepare_survey(bot=bot, message=m)
    except:
        log.exception(m)
        log.exception('Got exception on main handler')
        bot.send_message(m.chat.id,
                         'Что-то пошло не так')


@bot.message_handler(commands=['adminadminsendmessageadminadmin'])
def send_survey(m):
    try:
        menu_helper.send_text(bot=bot, message=m)
    except:
        log.exception(m)
        log.exception('Got exception on main handler')
        bot.send_message(m.chat.id,
                         'Что-то пошло не так')


@bot.message_handler(commands=['adminadminupdateusermenuadminadmin'])
def send_survey(m):
    try:
        menu_helper.update_user_menu(bot=bot, message=m)
    except:
        log.exception(m)
        log.exception('Got exception on main handler')
        bot.send_message(m.chat.id,
                         'Что-то пошло не так')


@bot.message_handler(commands=['adminadmingetstatsadminadmin'])
def get_stats(m):
    try:
        menu_helper.get_stats(bot=bot, message=m)
    except:
        log.exception(m)
        log.exception('Got exception on main handler')
        bot.send_message(m.chat.id,
                         'Что-то пошло не так')


@bot.message_handler(commands=['get_users_stat'])
def get_users_stat(m):
    try:
        menu_helper.get_users_stat(bot=bot, message=m)
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


@bot.callback_query_handler(func=lambda call: call.data[:6] == 'reply_')
def question_reply(call):
    try:
        menu_helper.question_reply(bot=bot, call=call)
    except:
        log.exception(call)
        log.exception('Got exception on main handler')
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')


@bot.callback_query_handler(func=lambda call: call.data[:9] == 'feedback_')
def question_reply(call):
    try:
        menu_helper.feedback_reply(bot=bot, call=call)
    except:
        log.exception(call)
        log.exception('Got exception on main handler')
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')


if __name__ == '__main__':
    p1 = Process(target=check_pending, args=(bot,))
    p1.start()
    # print('Listerning...')
    # bot.polling(none_stop=True)

    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    # Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    # Start aiohttp server
    web.run_app(
        app,
        host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=context,
    )


