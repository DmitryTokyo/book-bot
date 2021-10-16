from pathlib import Path

from environs import Env

env = Env()
env.read_env()

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


class Config(object):
    DEBUG = False
    TESTING = False
    URL = env('URL')
    ADMIN_TG_ID = env('ADMIN_TG_ID')
    REDIS_URL = env('REDIS_URL', 'redis://localhost:6379')
    URL_BOOKS_LIB = env('URL_BOOKS_LIB')
    YANDEX_SPELLER_URL = 'https://speller.yandex.net/services/spellservice.json/checkText'
    TOKEN = env('TG_TOKEN')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
