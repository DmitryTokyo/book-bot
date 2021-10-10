import os
from queue import Queue
from threading import Thread
from typing import TypeVar

from bot.telegram_logger import logger, TelegramLogsHandler
from config.config import Config
from flask import Flask, request, render_template
import telegram
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from bot.handler.user_handler import handle_users_reply

app: Flask = Flask(__name__)

if app.config['ENV'] == 'production':
    app.config.from_object('config.config.ProductionConfig')
else:
    app.config.from_object('config.config.DevelopmentConfig')


RenderTemplate = TypeVar('RenderTemplate')


bot: Bot = Bot(Config.TOKEN)
update_queue: Queue = Queue()


dispatcher: Dispatcher = Dispatcher(bot, update_queue)
thread: Thread = Thread(target=dispatcher.start, name='dispatcher')
thread.start()

dispatcher.add_handler(CommandHandler('start', handle_users_reply, pass_job_queue=True))
dispatcher.add_handler(CallbackQueryHandler(handle_users_reply, pass_job_queue=True))
dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply, pass_job_queue=True))
logger.addHandler(TelegramLogsHandler(bot, Config.ADMIN_TG_ID))
logger.info('Bot started work')


@app.route(f'/{Config.TOKEN}', methods=['POST'])
def webhook() -> str:
    if request.method == 'POST':
        update = telegram.update.Update.de_json(request.get_json(force=True), bot)
        update_queue.put(update)
        return 'ok'
    else:
        return 'not ok'


@app.route('/')
def check() -> RenderTemplate:
    return render_template('index.html', check='Well done!')


@app.route('/webhook', methods=['GET'])
def webhook_set() -> RenderTemplate:
    result = bot.setWebhook(f'{Config.URL}/{Config.TOKEN}')
    if result:
        os.makedirs('bot/files_storage/', exist_ok=True)
        return render_template('webhook.html', webhook='webhook setup ok!!!')
    else:
        return render_template('webhook.html', webhook='webhook setup failed')
