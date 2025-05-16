import logging
from logging.handlers import RotatingFileHandler

import telegram


class TelegramLogHandler(logging.Handler):
    """Отправляет ERROR-логи в указанный Telegram-чат."""

    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.bot.send_message(
                chat_id=self.chat_id,
                text=f"Лог {record.levelname}:\n{log_entry}",
            )
        except Exception as e:
            print(f"Ошибка отправки лога в Telegram: {e}")


def setup_logging(
    log_file_path: str,
    bot_token=None,
    chat_id=None,
) -> None:
    """
    Конфигурирует root-логгер:
    • вывод в консоль
    • ротация файла логов
    """
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=500_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    if bot_token and chat_id:
        tg_handler = TelegramLogHandler(bot_token, chat_id)
        tg_handler.setLevel(logging.ERROR)
        tg_handler.setFormatter(formatter)
        root_logger.addHandler(tg_handler)
