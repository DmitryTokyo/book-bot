import requests

url = 'https://speller.yandex.net/services/spellservice.json/checkText'


def check_speller(text):
    data = {
        'text': text,
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    if not response.json():
        return text
    
    for word in response.json():
        original_word = word['word']
        correct_word = word['s'][0]
        
        text = text.replace(original_word, correct_word)

    return text