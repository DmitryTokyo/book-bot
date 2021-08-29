import logging
from environs import Env
import redis
from redis import Redis

from bot.handler.book_keyboard import get_books_list_keyboard, get_book_detail_keyboard, get_book_file_keyboard
from bot.handler.book_keyboard import get_search_keyboard
from bot.handler.manage_books import get_cover_url
from bot.handler.notifications import (notify_admin_unsuccessful_search, notify_admin_non_exist_book, get_help_message,
                                       get_admin_error_message, get_user_error_message)
from config import config

_database = None
env = Env()
logger = logging.getLogger('book_bot')


def start(update, context, db=None):
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
        query.delete_message()
    else:
        chat_id = update.effective_chat.id
    search_markup = get_search_keyboard()
    context.bot.send_message(chat_id=chat_id, text='Напишите название книги', reply_markup=search_markup)
    return 'HANDLE_BOOKS_MENU'


def handle_books_menu(update, context, db) -> str:
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
        user_data = query.from_user
        message, reply_markup, is_found = get_books_list_keyboard(chat_id, db, menu_button=query.data)
        query.edit_message_text(message, reply_markup=reply_markup)
        book_name = db.get(f'request_{chat_id}')
    else:
        chat_id = update.effective_chat.id
        user_data = update.effective_user
        book_name = update.message.text
        message, reply_markup, is_found = get_books_list_keyboard(chat_id, db, book_name=book_name)
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    if not is_found:
        notify_admin_unsuccessful_search(user_data, book_name)
        return 'START'

    return 'HANDLE_BOOK'


def handle_book(update, context, db) -> str:
    query = update.callback_query
    try:
        chat_id = query.message.chat_id
    except AttributeError:
        return 'HANDLE_BOOKS_MENU'

    user_data = query.from_user
    if 'description' in query.data:
        __, book_url = query.data.split(',')
        message, reply_markup, book_name, is_available = get_book_detail_keyboard(book_url, db, need_description=True)
        query.edit_message_caption(caption=message, reply_markup=reply_markup)
    else:
        book_url = query.data
        message, reply_markup, book_name, is_available = get_book_detail_keyboard(book_url, db)
        query.delete_message()
        cover_url = get_cover_url(book_url, db)
        context.bot.send_photo(chat_id=chat_id, photo=cover_url, caption=message, reply_markup=reply_markup)
    if not is_available:
        notify_admin_non_exist_book(user_data, book_name)
    return 'HANDLE_DOWNLOAD_FILE'


def handle_download_file(update, context, db) -> str:
    query = update.callback_query
    chat_id = query.message.chat_id
    query.delete_message()
    context.bot.send_message(chat_id=chat_id, text='Подождите, книга скачивается')
    filename, book, reply_markup = get_book_file_keyboard(query.data, db)
    context.bot.send_document(chat_id=chat_id, document=book, filename=filename)
    return 'START'


def handle_help(update, context, db) -> str:
    message = get_help_message()
    update.message.reply_text(message)
    return 'START'


def handle_users_reply(update, context) -> str:
    db = get_database_connection()
    query = update.callback_query

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        user_data = update.effective_user
    elif query:
        user_reply = query.data
        chat_id = query.message.chat_id
        user_data = query.from_user
    else:
        return 'START'

    if user_reply in ['/start', 'Новый поиск']:
        user_state = 'START'
    elif 'prev' in user_reply or 'next' in user_reply:
        user_state = 'HANDLE_BOOKS_MENU'
    elif 'description' in user_reply:
        user_state = 'HANDLE_BOOK'
    elif user_reply == '/help':
        user_state = 'HELP'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': start,
        'HANDLE_BOOKS_MENU': handle_books_menu,
        'HANDLE_BOOK': handle_book,
        'HANDLE_DOWNLOAD_FILE': handle_download_file,
        'HELP': handle_help,
    }

    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context, db)
        db.set(chat_id, next_state)
    except Exception as err:
        error_admin_message = get_admin_error_message(user_data, chat_id, db)
        logger.error(error_admin_message)
        logger.exception(err)

        error_user_message = get_user_error_message(user_data)
        context.bot.send_message(chat_id=chat_id, text=error_user_message)
        return 'START'


def get_database_connection() -> Redis:
    global _database
    _database = redis.StrictRedis.from_url(config.REDIS_URL) if _database is None else _database
    return _database
