import logging
from environs import Env
from textwrap import dedent
import redis
from telegram import ReplyKeyboardMarkup

from bot.handler.book_keyboard import get_books_list_keyboard, get_book_detail_keyboard, get_book_file_keyboard
from bot.handler.book_keyboard import get_search_keyboard
from bot.handler.manage_books import get_cover_url


_database = None
env = Env()
logger = logging.getLogger('book_bot')


def start(update, context, db):
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
        query.delete_message()
    else:
        chat_id = update.effective_chat.id
    search_markup = get_search_keyboard()
    context.bot.send_message(chat_id=chat_id, text='Напишите название книги', reply_markup=search_markup)
    return 'HANDLE_BOOKS_MENU'


def handle_books_menu(update, context, db):
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
        user_data = query.from_user
        message, reply_markup, is_found = get_books_list_keyboard(chat_id, db, menu_button=query.data)
        query.edit_message_text(message, reply_markup=reply_markup)
    else:
        chat_id = update.effective_chat.id
        user_data = update.effective_user
        book_name = update.message.text
        message, reply_markup, is_found = get_books_list_keyboard(chat_id, db, book_name=book_name)
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    if not is_found:
        notify_unsuccessful_search(context, user_data, book_name)
    return 'HANDLE_BOOK'


def handle_book(update, context, db):
    query = update.callback_query
    try:
        chat_id = query.message.chat_id
    except AttributeError:
        return 'HANDLE_BOOKS_MENU'

    user_data = query.from_user
    if 'description' in query.data:
        __, book_url = query.data.split(',')
        message, reply_markup, bookname, is_available = get_book_detail_keyboard(book_url, db, need_description=True)
        query.edit_message_caption(caption=message, reply_markup=reply_markup)
    else:
        book_url = query.data
        message, reply_markup, bookname, is_available = get_book_detail_keyboard(book_url, db)
        query.delete_message()
        cover_url = get_cover_url(book_url, db)
        context.bot.send_photo(chat_id=chat_id, photo=cover_url, caption=message, reply_markup=reply_markup)
    if not is_available:
        notify_unexist_book(context, user_data, bookname)
    return 'HANDLE_DOWNLOAD_FILE'


def handle_download_file(update, context, db):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.delete_message()
    context.bot.send_message(chat_id=chat_id, text='Подождите, книга скачивается')
    filename, book, reply_markup = get_book_file_keyboard(query.data, db)
    context.bot.send_document(chat_id=chat_id, document=book, filename=filename)
    return 'START'


def handle_help(update, context, db):
    message = dedent('''
    Я помогаю находить тебе бесплатные книги в сети.
    Книги я присылаю в формате epub, поэтому если твоя
    читалка не поддерживает данный формат, нужно скачать другую.
    
    Основные команды:
    /start - Для начала работы со мной нажми
    ''')
    update.message.reply_text(message)
    return 'START'


def notify_unsuccessful_search(context, user_data, book_name):
    message = dedent(f'''
        Поиск книги по запросу -  {book_name} не удался

        user_id - {user_data.id}
        username - {user_data.username}
        firstname - {user_data.first_name}
        ''')
    logger.warning(message)


def notify_unexist_book(context, user_data, book_name):
    message = dedent(f'''
        Доступ к книге - {book_name} закрыт

        user_id - {user_data.id}
        username - {user_data.username}
        firstname - {user_data.first_name}
        ''')
    logger.warning(message)


def notify_if_got_error(context):
    pass


def handle_users_reply(update, context):
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
        return

    if user_reply == '/start' or user_reply == 'Новый поиск':
        user_state = 'START'
    elif 'prev' in user_reply or 'next' in user_reply:
        user_state = 'HANDLE_BOOKS_MENU'
    elif 'description' in user_reply:
        user_state = 'HANDLE_BOOK'
    elif user_reply == '/help':
        user_state = 'HELP'
    else:
        user_state = db.get(chat_id).decode("utf-8")

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
        message = dedent(f'''
        Bot got error
        user_id - {user_data.id}
        username - {user_data.username}
        firstname - {user_data.first_name}
        request - {db.get(f'request_{chat_id}')}
        ''')
        logger.error(message)
        logger.exception(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = env("DATABASE_PASSWORD")
        database_host = env("DATABASE_HOST")
        database_port = env("DATABASE_PORT")

        _database = redis.Redis(host=database_host,
                                port=database_port,
                                password=database_password)
    return _database
