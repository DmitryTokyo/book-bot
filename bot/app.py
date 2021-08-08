import logging
from queue import Queue
from threading import Thread

from environs import Env
from flask import Flask, request, render_template
import telegram
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from bot.handler.user_handler import handle_users_reply

app = Flask(__name__)
env = Env()
env.read_env()

logger = logging.getLogger('book_bot')
logger.setLevel(logging.INFO)

TOKEN = env('TG_TOKEN_TEST')  # Test token
URL = env('URL')
ADMIN_TG_ID = env('ADMIN_TG_ID')
bot = Bot(TOKEN)
update_queue = Queue()


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot: Bot, user_id: int) -> None:
        super().__init__()
        self.chat_id = user_id
        self.bot = bot

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


dispatcher = Dispatcher(bot, update_queue)
thread = Thread(target=dispatcher.start, name='dispatcher')
thread.start()

dispatcher.add_handler(CommandHandler('start',  handle_users_reply, pass_job_queue=True))
dispatcher.add_handler(CallbackQueryHandler(handle_users_reply, pass_job_queue=True))
dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply, pass_job_queue=True))
logger.addHandler(TelegramLogsHandler(bot, ADMIN_TG_ID))
logger.info('Bot started work')


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = telegram.update.Update.de_json(request.get_json(force=True), bot)
        update_queue.put(update)
        return 'ok'
    except Exception as e:
        logging.critical(e)


@app.route('/')
def check():
    return render_template('index.html', check='Well done!')


@app.route('/webhook', methods=['GET'])
def webhook_set():
    s = bot.setWebhook(f'{URL}/{TOKEN}')
    if s:
        return render_template('webhook.html', webhook='webhook setup ok!!!')
    else:
        return render_template('webhook.html', webhook='webhook setup failed')
