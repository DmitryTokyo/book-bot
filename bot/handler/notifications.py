import logging
from textwrap import dedent


logger = logging.getLogger('book_bot')


def notify_admin_unsuccessful_search(user_data, book_name):
    message = dedent(f'''
        Поиск книги по запросу -  {book_name} не удался

        user_id - {user_data.id}
        username - {user_data.username}
        firstname - {user_data.first_name}
        ''')
    logger.warning(message)


def notify_admin_non_exist_book(user_data, book_name):
    message = dedent(f'''
        Доступ к книге - {book_name} закрыт

        user_id - {user_data.id}
        username - {user_data.username}
        firstname - {user_data.first_name}
        ''')
    logger.warning(message)


def get_help_message():
    return dedent(
        '''
        Я помогаю находить тебе бесплатные книги в сети.
        Книги я присылаю в формате epub, поэтому если твоя
        читалка не поддерживает данный формат, нужно скачать другую.
    
        Основные команды:
        /start - Для начала работы со мной нажми'''
    )


def get_did_not_find_message(book_name):
    return dedent(
        f'''
        К сожалению по запросу {book_name}
        ничего не нашлось.

        Для нового поиска воспользуйся кнопкой

        "Новый поиск"

        ⬇️⬇️⬇️⬇️'''
    )


def get_limited_access_book_message():
    return dedent(
        '''
        Доступ к бесплатной книге ограничен 😢🙅🏻‍♂️

        Для нового поиска воспользуйся кнопкой

        "Новый поиск"

        ⬇️⬇️⬇️⬇️'''
    )


def get_admin_error_message(user_data, chat_id, db):
    return dedent(
        f'''
        Bot got error
        user_id - {user_data.id}
        username - {user_data.username}
        firstname - {user_data.first_name}
        request - {db.get(f'request_{chat_id}')}'''
    )


def get_user_error_message(user_data):
    return dedent(
        f'''
        Что-то пошло не так.
        {user_data.username}
        Попробуй выполнить поиск еще раз
        
        Начни с кнопки в меню
        
        "Новый поиск"'''
    )
