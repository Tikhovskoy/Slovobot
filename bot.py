import logging
import os

from environs import Env
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from dialogflow_utils import detect_intent_text
from logging_utils import setup_logging

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Здравствуйте")

def dialogflow_handler(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
    project_id = context.bot_data.get("DIALOGFLOW_PROJECT_ID")
    language_code = "ru"

    try:
        fulfillment_text, is_fallback = detect_intent_text(
            text=text,
            user_id=user_id,
            project_id=project_id,
            language_code=language_code,
        )
        logger.info(
            f"TG | User {user_id}: '{text}' -> '{fulfillment_text}', fallback={is_fallback}"
        )
        response_text = fulfillment_text
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

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials
    setup_logging(log_file_path)

    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.bot_data["DIALOGFLOW_PROJECT_ID"] = google_project_id

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, dialogflow_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
