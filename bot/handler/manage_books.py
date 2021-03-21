import os
import json
import re
import requests
from urllib.parse import urljoin
from environs import Env

env = Env()


def get_cover_url(book_url, db):
    os.makedirs('bot/books/', exist_ok=True)
    book_id = os.path.basename(book_url)
    book = json.loads(db.get(f'book_{book_id}'))
    if book['cover_link']:
        cover_path = f'bot/books/cover_{book_id}.jpg'
        if not os.path.exists(cover_path):
            download_cover(book_id, cover_path, book['cover_link'])
    else:
        cover_path = 'bot/static/default_cover.png'

    with open(cover_path, 'rb') as file:
        image_file = file.read()
    return image_file


def get_book(book_file_link, db):
    os.makedirs('bot/books/', exist_ok=True)
    book_file_link, book_id = book_file_link.split(',')
    book = json.loads(db.get(f'book_{book_id}'))
    if 'book_filename' in book:
        book_file_path = f'bot/books/{book["book_filename"]}'
        if os.path.exists(book_file_path):
            with open(book_file_path, 'rb') as file:
                book_file = file.read()
            return book['book_filename'], book_file

    response = requests.get(book_file_link, stream=True)
    response.raise_for_status()
    book_filename = get_filename(response)
    download_book(response, book_filename)
    book['book_filename'] = book_filename
    db.set(f'book_{book_id}', json.dumps(book))
    return book_filename, response.content


def get_filename(response):
    filename = response.headers['Content-Disposition']
    filename = re.split(r'.*filename=', filename)[1]
    if '.fb2' in filename:
        filename = filename.replace('.fb2', '').strip('"')
    filename = filename.strip('"')
    return filename


def download_book(response, filename):
    full_path = urljoin('bot/books/', filename)
    with open(full_path, 'wb') as file:
        file.write(response.content)


def download_cover(book_id, cover_path, cover_url):
    response = requests.get(cover_url, stream=True)
    response.raise_for_status()

    with open(cover_path, 'wb') as file:
        file.write(response.content)