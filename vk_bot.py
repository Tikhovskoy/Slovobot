import os
import logging
import random

from environs import Env
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from google.api_core.exceptions import GoogleAPICallError

from dialogflow_utils import detect_intent_text
from logging_utils import setup_logging

logger = logging.getLogger(__name__)


def reply_with_dialogflow(event, vk_api_client, project_id):
    text = event.text
    raw_user_id = event.user_id
    user_id = f"vk-{raw_user_id}"

    try:
        response, is_fallback = detect_intent_text(
            text,
            user_id,
            project_id,
            "ru",
        )
    except GoogleAPICallError as e:
        logger.error(
            "Dialogflow недоступен для VK user %s: %s",
            user_id,
            e,
            exc_info=True,
        )
        vk_api_client.messages.send(
            user_id=raw_user_id,
            message="Сервис временно недоступен, попробуйте позже.",
            random_id=random.randint(1, 1_000_000_000),
        )
        return

    if is_fallback:
        logger.info(
            "VK | User %s: '%s' -> fallback, бот молчит",
            user_id,
            text,
        )
        return

    try:
        vk_api_client.messages.send(
            user_id=raw_user_id,
            message=response,
            random_id=random.randint(1, 1_000_000_000),
        )
        logger.info(
            "VK | User %s: '%s' -> '%s'",
            user_id,
            text,
            response,
        )
    except vk_api.ApiError as e:
        logger.error(
            "Не удалось отправить сообщение VK пользователю %s: %s",
            user_id,
            e,
            exc_info=True,
        )


def main() -> None:
    env = Env()
    env.read_env()
    credentials = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials

    vk_token = env.str("VK_GROUP_TOKEN")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")
    telegram_token = env.str("TELEGRAM_TOKEN")
    telegram_chat_id = env.str("TELEGRAM_CHAT_ID")

    log_file = "logs/vk_bot.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    setup_logging(
        log_file_path=log_file,
        bot_token=telegram_token,
        chat_id=telegram_chat_id,
    )

    vk_session = vk_api.VkApi(token=vk_token)
    vk_client = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK bot с DialogFlow запущен!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reply_with_dialogflow(event, vk_client, project_id)


if __name__ == "__main__":
    main()
