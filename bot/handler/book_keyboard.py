import json
import os
from textwrap import dedent
from more_itertools import chunked
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from bot.handler.check_text import get_checking_by_speller
from bot.handler.notifications import get_did_not_find_message, get_limited_access_book_message
from bot.parser.book import get_books_list, get_book_info, is_book_available
from bot.handler.manage_books import get_book


def get_books_list_keyboard(chat_id, db, book_name=None, menu_button=None):
    if book_name:
        book_name = get_checking_by_speller(book_name)
        books = get_books_list(book_name)
        db.set(f'books_{chat_id}', json.dumps(books))  # Заношу в базу найденные книги по запросу
        db.set(f'request_{chat_id}', book_name)  # Заношу запрос пользователя в базу
    else:
        books = json.loads(db.get(f'books_{chat_id}'))

    if not books:
        message = get_did_not_find_message(book_name)
        search_keyboard = get_search_keyboard()
        is_found = False
        return message, search_keyboard, is_found

    books_pages = list(chunked(books, 4))
    max_page_index = len(books_pages)

    if not menu_button:
        page_number = 1
    else:
        __, page_number = menu_button.split(',')
        page_number = int(page_number)

    # С какой книги по счету начинается вывод на странице
    book_number_on_page = page_number * 4 - 3

    message = ''
    books_keyboard = []
    for count, book in enumerate(books_pages[page_number - 1], start=book_number_on_page):
        books_keyboard.append([InlineKeyboardButton(f'Книга {count}', callback_data=book['book_url'])])
        message += dedent(
            f'{count}. - {book["title"]}\n',
        )

    if max_page_index > 1:
        if page_number == 1:
            books_keyboard.append([
                InlineKeyboardButton(f'стр {page_number + 1} ->', callback_data=f'next,{page_number + 1}'),
            ])
        elif page_number == max_page_index:
            books_keyboard.append([
                InlineKeyboardButton(f'<- стр {page_number - 1}', callback_data=f'prev,{page_number - 1}'),
            ])
        else:
            books_keyboard.append([
                InlineKeyboardButton(f'<- стр {page_number - 1}', callback_data=f'prev,{page_number - 1}'),
                InlineKeyboardButton(f'стр {page_number + 1} ->', callback_data=f'prev,{page_number + 1}'),
            ])
    message = f'Найденная книга\n{message}' if len(books_pages[0]) == 1 else f'Найденные книги \n{message}'

    is_found = True
    return message, InlineKeyboardMarkup(books_keyboard), is_found


def get_book_detail_keyboard(book_url, db, need_description=False):
    book_id = os.path.basename(book_url)

    try:
        book = json.loads(db.get(f'book_{book_id}'))
    except TypeError:
        book = get_book_info(book_url)
        db.set(f'book_{book_id}', json.dumps(book))

    book_file_link = book['book_file_link']
    is_available = is_book_available(book_file_link)
    if not is_available:
        message = get_limited_access_book_message()
        search_keyboard = get_search_keyboard()
        return message, search_keyboard, book['title'], is_available

    message = book['title']
    description = book['description']
    book_keyboard = []
    if description:
        if need_description:
            message = message + '\n\n' + description
        book_keyboard = [
            [InlineKeyboardButton('описание', callback_data=f'description,{book_url}')],
        ]
    book_keyboard.append([
        InlineKeyboardButton(
            f'Скачать книгу {book["type"]}', callback_data=f'{book_file_link},{book_id}',
        ),
    ])

    return message, InlineKeyboardMarkup(book_keyboard), book['title'], is_available


def get_book_file_keyboard(book_file_link, db):
    book, book_file = get_book(book_file_link, db)
    search_keyboard = get_search_keyboard()
    return book, book_file, search_keyboard


def get_search_keyboard():
    search_keyboard = [['Новый поиск']]
    search_markup = ReplyKeyboardMarkup(search_keyboard, one_time_keyboard=True, resize_keyboard=True)
    return search_markup
