import os
import logging

from environs import Env
from google.api_core.exceptions import GoogleAPICallError
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
    except GoogleAPICallError as e:
        logger.error("Dialogflow недоступен: %s", e, exc_info=True)
        response_text = "Сервис временно недоступен, попробуйте позже."
    else:
        logger.info(
            "TG | User %s: '%s' -> '%s', fallback=%s",
            user_id,
            text,
            fulfillment_text,
            is_fallback,
        )
        response_text = fulfillment_text

    update.message.reply_text(response_text)


def main() -> None:
    env = Env()
    env.read_env()

    telegram_token = env.str("TELEGRAM_TOKEN")
    telegram_chat_id = env.str("TELEGRAM_CHAT_ID")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    log_file = "logs/bot.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    setup_logging(
        log_file_path=log_file,
        bot_token=telegram_token,
        chat_id=telegram_chat_id,
    )

    updater = Updater(telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.bot_data["DIALOGFLOW_PROJECT_ID"] = project_id

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, dialogflow_handler)
    )

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
