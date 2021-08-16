import json
import random
from typing import Optional

import requests
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from config import config

BookLib = list[dict[str, str]]


def get_books_list(book_name: str) -> Optional[BookLib]:
    response = _make_request(config.URL_BOOKS_LIB, book_name=book_name)

    if not response:
        return None

    soup = BeautifulSoup(response, 'lxml')

    title = soup.find('h3', string=re.compile('Найденные книги'))
    if not title:
        return None

    books = title.find_next('ul')
    books_lib = []
    for book in books.find_all('li'):
        book_link = book.find('a', href=True)['href']
        book_title = book.text
        books_lib.append({
            'title': book_title,
            'book_url': urljoin(config.URL_BOOKS_LIB, book_link),
        })

    return books_lib


def get_book_info(book_link: str):
    response = _make_request(book_link)
    if not response:
        return None

    soup = BeautifulSoup(response, 'lxml')

    title = soup.find(id='main').h1.text
    title = title.split('(')[0].strip()
    book_info = {
        'title': title,
        'book_link': book_link,
        'book_file_link': None,
    }
    book_description_tag = soup.find(id='main').find('h2', string=re.compile('Аннотация'))

    book_info['description'] = (
        book_description_tag.find_next('p').text
        if not book_description_tag.find_next(string=re.compile('отсутствует'))
        else None
    )

    book_size_tags = soup.find(id='main').find('span', style='size')
    book_a_tags = book_size_tags.find_all_next('a')

    for book_a_tag in book_a_tags[:4]:
        if re.search(r'epub', book_a_tag.text):
            book_info['type'] = 'epub'
        if re.search(r'pdf', book_a_tag.text):
            book_info['type'] = 'pdf'
        if re.search(r'djvu', book_a_tag.text):
            book_info['type'] = 'djvu'

        if 'type' in book_info:
            link = book_a_tag['href']
            book_info['book_file_link'] = urljoin(book_link, link)
            break

    try:
        cover_link = soup.find(alt='Cover image')['src']
        book_info['cover_link'] = urljoin(book_link, cover_link)
    except TypeError:
        book_info['cover_link'] = None

    return book_info


def is_book_available(link):
    response = requests.head(link)
    return True if response.headers.get('Location') else False


def get_user_agent():
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
        book_name: str = None,
) -> Optional[str]:
    headers = {'User-Agent': get_user_agent()}

    params = {'ask': book_name} if book_name else None
    response = getattr(requests, method)(url, headers=headers, params=params)

    if not response.ok:
        return None

    return response.text
