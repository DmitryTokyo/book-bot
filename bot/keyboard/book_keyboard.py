import json
from textwrap import dedent
from more_itertools import chunked
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from bot.utils.check_speller import get_checking_by_speller
from bot.utils.notifications import get_did_not_find_message
from bot.parser.parse_book import find_book_download_url, find_books_on_user_request, get_book_file_info


def get_books_list_keyboard(user_id, db, book_name=None, menu_button=None):
    is_found = True
    max_books_numbers_on_page = 4
    if book_name:  # This means first request from user
        book_name = get_checking_by_speller(book_name)
        db.set(f'request_{user_id}', book_name)
        db.delete(f'books{user_id}')  # Remove user previous request
        find_books_on_user_request(book_name, user_id, db)

    books = json.loads(db.get(f'books{user_id}'))
    if not books:
        message = get_did_not_find_message(book_name)
        search_keyboard = get_search_keyboard()
        is_found = False
        return message, search_keyboard, is_found

    books_pages = list(chunked(books, max_books_numbers_on_page))
    max_page_index = len(books_pages)

    if not menu_button:
        page_number = 1
    else:
        __, page_number = menu_button.split(',')
        page_number = int(page_number)

    start_book_number_on_page = page_number * max_books_numbers_on_page - 3  # What book number keyboard start

    message = ''
    books_keyboard = []
    for count, book in enumerate(books_pages[page_number - 1], start=start_book_number_on_page):
        books_keyboard.append([InlineKeyboardButton(f'Книга {count}', callback_data=str(book['book_id']))])
        author = book.get('author')
        title = book.get('title')
        message += dedent(
            f'{count}. {author} - {title}\n',
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

    return message, InlineKeyboardMarkup(books_keyboard), is_found


def get_book_detail_keyboard(book_id, user_id, db):
    books = json.loads(db.get(f'books{user_id}'))
    user_chosen_book = next(filter(lambda book: book['book_id'] == book_id, books))

    if not db.exists(f'book_{book_id}'):
        find_book_download_url(user_chosen_book, book_id, db)

    book = json.loads(db.get(f'book_{book_id}'))
    title = book['title']
    book_keyboard: list = [[
        InlineKeyboardButton(
            f'Скачать книгу {title}', callback_data=str(book_id),
        ),
    ]]

    return title, InlineKeyboardMarkup(book_keyboard)


def get_book_file_keyboard(book_id, db):
    search_keyboard = get_search_keyboard()
    book_file_info = get_book_file_info(book_id, db)
    if not book_file_info:
        return None, None, search_keyboard

    return book_file_info['filename'], book_file_info['book_file'], search_keyboard


def get_search_keyboard():
    search_keyboard = [['Новый поиск']]
    search_markup = ReplyKeyboardMarkup(search_keyboard, one_time_keyboard=True, resize_keyboard=True)
    return search_markup
