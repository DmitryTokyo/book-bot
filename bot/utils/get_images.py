import json
import os

import requests


def get_cover_image(book_url, db):
    book_id = os.path.basename(book_url)
    book = json.loads(db.get(f'book_{book_id}'))
    if book.get('cover_link'):
        cover_path = f'bot/books/cover_{book_id}.jpg'
        if not os.path.exists(cover_path):
            download_cover(cover_path, book['cover_link'])
    else:
        cover_path = 'bot/static/default_cover.png'

    with open(cover_path, 'rb') as file:
        image_file = file.read()
    return image_file


def download_cover(cover_path, cover_url):
    response = requests.get(cover_url, stream=True)
    response.raise_for_status()

    with open(cover_path, 'wb') as file:
        file.write(response.content)