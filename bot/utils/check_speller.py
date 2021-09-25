import requests

from config.config import Config


def get_checking_by_speller(text: str) -> str:
    data = {'text': text}
    response = getattr(requests, 'post')(
        Config.YANDEX_SPELLER_URL,
        data=data or {},
    )

    if not response.ok or not response.json():
        return text

    correct_text: str = ''
    for word in response.json():
        original_word = word['word']
        correct_word = word['s'][0]

        correct_text = text.replace(original_word, correct_word)

    return correct_text
