import logging
from textwrap import dedent


logger = logging.getLogger('book_bot')


def notify_admin_unsuccessful_search(user_data, book_name) -> None:
    message = dedent(
        f'Поиск книги по запросу -  {book_name} не удался\n'
        f'user_id - {user_data.id}'
        f'username - {user_data.username}'
        f'firstname - {user_data.first_name}',
    )
    logger.warning(message)


def notify_admin_non_exist_book(user_data, book_name) -> None:
    message = dedent(
        f'Доступ к книге - {book_name} закрыт\n'
        f'user_id - {user_data.id}'
        f'username - {user_data.username}'
        f'firstname - {user_data.first_name}',
    )
    logger.warning(message)


def get_help_message() -> str:
    return dedent(
        'Я помогаю находить тебе бесплатные книги в сети.'
        'Книги я присылаю в формате epub, поэтому если твоя'
        'читалка не поддерживает данный формат, нужно скачать другую.\n'
        'Основные команды:'
        '/start - Для начала работы со мной нажми',
    )


def get_did_not_find_message(book_name: str) -> str:
    return dedent(
        f'К сожалению по запросу:\n{book_name}\n'
        f'ничего не нашлось.\n\n'
        f'Для нового поиска воспользуйся кнопкой\n'
        f'"Новый поиск"\n'
        f'⬇️⬇️⬇️⬇️',
    )


def get_admin_error_message(user_data, chat_id: int, db) -> str:
    user_request = db.get(f'request_{chat_id}').decode('utf-8')
    return dedent(
        f'Bot got error\n'
        f'user_id - {user_data.id}\n'
        f'username - {user_data.username}\n'
        f'firstname - {user_data.first_name}\n'
        f'request - {user_request}',
    )


def get_user_error_message(user_data) -> str:
    return dedent(
        f'Что-то пошло не так.\n'
        f'{user_data.username} '
        f'Попробуй выполнить поиск еще раз\n\n'
        f'Начни с кнопки в меню\n'
        f'"Новый поиск"',
    )
