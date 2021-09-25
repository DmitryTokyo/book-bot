import json
import os
import random
from typing import Optional

import requests
import re
from urllib.parse import urljoin
from pathlib import PurePath
from bs4 import BeautifulSoup

from config.config import Config

BookLib = list[dict[str, str]]


def find_books_on_user_request(book_name: str, user_id, db) -> None:
    base_url = Config.URL_BOOKS_LIB
    search_books_url = urljoin(base_url, 'booksearch')
    params = {'ask': book_name}
    response = _make_request(search_books_url, params=params)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    title = soup.find('h3', string=re.compile('Найденные книги'))
    if not title:
        return None
    books = _extract_books_info_from_request(soup, base_url)
    db.set(f'books{user_id}', json.dumps(books))


def _extract_books_info_from_request(soup, base_url):
    books = []
    books_divs = soup.find('div', class_='wrap').find_all('div', class_='item')
    for book_div in books_divs:
        book_mini_cover_img_url = book_div.find('div', class_='cover').img['src']
        book_id = PurePath(book_mini_cover_img_url).stem
        book_page_url = book_div.find('div', class_='cover').a['href']
        book_author = book_div.find('span', class_='author').a['title']
        book_title = book_div.find('div', class_='book_name').a.text
        book = {
            'book_id': book_id,
            'book_page_url': urljoin(base_url, f'{book_page_url}/d'),
            'book_mini_cover_img_url': urljoin(base_url, book_mini_cover_img_url),
            'author': book_author,
            'title': book_title,
        }
        books.append(book)
    return books


def find_book_download_url(book: dict, book_id: int, db) -> None:
    book_page_url = book.get('book_page_url')
    params = {'f': 'epub'}
    response = _make_request(book_page_url, params=params)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'lxml')
    book_download_div = soup.find('div', class_='b_download_progress_txt')
    book_file_url = f'https:{book_download_div.a["href"]}'
    book['book_file_url'] = book_file_url
    db.set(f'book_{book_id}', json.dumps(book))


def get_book_file_info(book_id, db):
    book = json.loads(db.get(f'book_{book_id}'))

    if book.get('local_file_path'):
        book_local_file_path = book.get('local_file_path')
        if os.path.exists(book_local_file_path):
            with open(book_local_file_path, 'rb') as file:
                book_file = file.read()
                book_file_info = {
                    'book_file': book_file,
                    'filename': book.get('filename')
                }
            return book_file_info
    response = _make_request(book['book_file_url'], stream=True)

    if not response:
        return None

    book_filename_search_result = re.search('(?<=[t/])\w*(.epub)', book['book_file_url'])

    if not book_filename_search_result:
        return None

    book_filename = book_filename_search_result.group(0)

    book_local_file_path = urljoin('bot/files_storage/', book_filename)
    book_file = response.content

    with open(book_local_file_path, 'wb') as file:
        file.write(book_file)

    book |= {'book_local_file_path': book_local_file_path, 'filename': book_filename}

    db.set(f'book_{book_id}', json.dumps(book))
    book_file_info = {
        'book_file': book_file,
        'filename': book.get('filename')
    }
    return book_file_info


def is_book_available(link):
    response = requests.get(link)
    return bool(response.headers.get('Content-Length'))


def _get_user_agent():
    """
    This function is working while fake-useragent lib
    has the bug
    """
    with open('bot/parser/user_agent/user_agent.json', 'r') as file:
        user_agents = json.load(file)
        return random.choice(user_agents)


def _make_request(
        url: str,
        method: str = 'get',
        params: dict = None,
        stream=False,
) -> Optional[str]:
    headers = {'User-Agent': _get_user_agent()}

    params = params
    response = getattr(requests, method)(url, headers=headers, params=params, stream=stream)

    if not response.ok:
        return None
    return response
