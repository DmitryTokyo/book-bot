import logging
from queue import Queue
from threading import Thread

from environs import Env
from flask import Flask, request, send_from_directory
from flask_sslify import SSLify
import telegram
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from bot.handler.user_handler import handle_users_reply

app = Flask(__name__)
env = Env()

TOKEN = env('TG_TOKEN')
URL = env('URL')
bot = Bot(TOKEN)
update_queue = Queue()

dispatcher = Dispatcher(bot, update_queue)
thread = Thread(target=dispatcher.start, name='dispatcher')
thread.start()

dispatcher.add_handler(CommandHandler('start',  handle_users_reply, pass_job_queue=True))
dispatcher.add_handler(CallbackQueryHandler(handle_users_reply, pass_job_queue=True))
dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply, pass_job_queue=True))


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = telegram.update.Update.de_json(request.get_json(force=True), bot)
        update_queue.put(update)
        return 'ok'
    except Exception as e:
        logging.critical(e)


@app.route('/check')
def check():
    return '<h1>Works well</h1>'


@app.route('/', methods=['GET'])
def webhook_set():
    s = bot.setWebhook(f'{URL}/{TOKEN}')
    if s:
        return "webhook setup ok!!!"
    else:
        return "webhook setup failed"