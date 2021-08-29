from environs import Env

env = Env()
env.read_env()

TOKEN = env('TG_TOKEN')
URL = env('URL')
ADMIN_TG_ID = env('ADMIN_TG_ID')
REDIS_URL = env('REDIS_URL', 'redis://localhost:6379')

URL_BOOKS_LIB = env('URL_BOOKS_LIB')

YANDEX_SPELLER_URL = 'https://speller.yandex.net/services/spellservice.json/checkText'
