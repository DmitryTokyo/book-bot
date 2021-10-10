from telegram import Bot

import logging


logger = logging.getLogger('book_bot')
logger.setLevel(logging.INFO)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot: Bot, user_id: int) -> None:
        super().__init__()
        self.chat_id = user_id
        self.bot = bot

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)
