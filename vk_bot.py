import os
import logging
from logging.handlers import RotatingFileHandler
import random
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
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

def reply_with_dialogflow(event, vk_api, project_id):
    text = event.text
    user_id = event.user_id

    try:
        response, is_fallback = detect_intent_text(
            text=text,
            user_id=user_id,
            project_id=project_id,
            language_code="ru"
        )
        if is_fallback:
            logger.info(f"VK | User {user_id}: '{text}' -> fallback, бот молчит")
            return
        vk_api.messages.send(
            user_id=user_id,
            message=response,
            random_id=random.randint(1, 1_000_000_000)
        )
        logger.info(f"VK | User {user_id}: '{text}' -> '{response}'")
    except Exception as e:
        vk_api.messages.send(
            user_id=user_id,
            message="Извините, произошла ошибка.",
            random_id=random.randint(1, 1_000_000_000)
        )
        logger.error(f"DialogFlow error for user {user_id}: {e}", exc_info=True)

def main():
    env = Env()
    env.read_env()
    vk_group_token = env.str("VK_GROUP_TOKEN")
    dialogflow_project_id = env.str("DIALOGFLOW_PROJECT_ID")
    google_credentials = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    log_file_path = os.path.join("logs", "vk_bot.log")

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials

    setup_logging(log_file_path)

    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK bot с DialogFlow запущен!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reply_with_dialogflow(event, vk_api, dialogflow_project_id)

if __name__ == "__main__":
    main()
