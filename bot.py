import os
import logging
from logging.handlers import RotatingFileHandler
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env

from dialogflow_utils import detect_intent_text

logger = logging.getLogger(__name__)

def setup_logging(log_file_path: str) -> None:
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=500_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Здравствуйте")

def dialogflow_handler(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
    project_id = context.bot_data.get("DIALOGFLOW_PROJECT_ID")
    language_code = "ru"

    try:
        response_text = detect_intent_text(text, user_id, project_id, language_code)
        logger.info(f"User {user_id}: '{text}' -> '{response_text}'")
    except Exception as e:
        logger.error(f"DialogFlow error: {e}", exc_info=True)
        response_text = "Извините, не удалось получить ответ."

    update.message.reply_text(response_text)

def main():
    env = Env()
    env.read_env()
    telegram_token = env.str("TELEGRAM_TOKEN")
    google_project_id = env.str("DIALOGFLOW_PROJECT_ID")
    google_credentials = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    log_file_path = os.path.join("logs", "bot.log")

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials

    setup_logging(log_file_path)

    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.bot_data["DIALOGFLOW_PROJECT_ID"] = google_project_id

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, dialogflow_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
