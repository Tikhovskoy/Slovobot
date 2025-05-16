import json
import os
import logging

from environs import Env
from google.cloud import dialogflow_v2 as dialogflow

from logging_utils import setup_logging


def load_intents_map(project_id):
    """
    Загружает все существующие интенты агента
    и возвращает словарь {display_name: IntentResource}.
    """
    client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    existing = client.list_intents(request={"parent": parent})
    return {intent.display_name: intent for intent in existing}


def make_intent_object(display_name, training_phrases_parts, message_texts):
    """
    Строит объект Intent с указанным display_name,
    вариантами фраз и ответами.
    """
    training_phrases = []
    for phrase in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrases.append(
            dialogflow.Intent.TrainingPhrase(parts=[part])
        )

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )
    return intent


def upsert_intents_from_file(project_id, json_path, language_code="ru"):
    """
    Создает или обновляет интенты по данным из JSON-файла.
    Если display_name уже существует, обновляет, иначе — создаёт.
    """
    client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    existing = load_intents_map(project_id)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    to_create = []
    to_update = []

    for intent_name, value in data.items():
        training_phrases = value.get("questions", [])
        answer = value.get("answer", "")
        intent_obj = make_intent_object(
            display_name=intent_name,
            training_phrases_parts=training_phrases,
            message_texts=[answer],
        )

        if intent_name in existing:
            intent_obj.name = existing[intent_name].name
            to_update.append(intent_obj)
        else:
            to_create.append(intent_obj)

    if to_update:
        logging.info(
            "Updating %d intents: %s",
            len(to_update),
            [i.display_name for i in to_update],
        )
        client.batch_update_intents(
            request={
                "parent": parent,
                "intents": to_update,
                "language_code": language_code,
            }
        ).result()

    if to_create:
        logging.info(
            "Creating %d intents: %s",
            len(to_create),
            [i.display_name for i in to_create],
        )
        client.batch_create_intents(
            request={
                "parent": parent,
                "intents": to_create,
                "language_code": language_code,
            }
        ).result()

    logging.info(
        "Completed: created %d, updated %d intents.",
        len(to_create),
        len(to_update),
    )


def main() -> None:
    """Чтение .env, настройка логирования и запуск upsert."""
    env = Env()
    env.read_env()
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "create_intents.log")
    setup_logging(log_file)

    upsert_intents_from_file(
        project_id,
        json_path="questions.json",
        language_code="ru",
    )


if __name__ == "__main__":
    main()
