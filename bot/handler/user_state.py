from typing import Optional

from redis import Redis


def get_user_state(user_reply: str, chat_id: str, db: Redis) -> str:
    if user_reply in ['/start', 'Новый поиск']:
        user_state = 'START'
    elif 'prev' in user_reply or 'next' in user_reply:
        user_state = 'HANDLE_BOOKS_MENU'
    elif user_reply == '/help':
        user_state = 'HELP'
    else:
        user_raw_state: Optional[bytes] = db.get(chat_id)
        user_state = user_raw_state.decode('utf-8') if user_raw_state and isinstance(user_raw_state, bytes) else 'START'

    return user_state
