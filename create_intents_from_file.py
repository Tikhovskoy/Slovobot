import os
import json
from google.cloud import dialogflow_v2 as dialogflow
from environs import Env

def create_intent(project_id, display_name, training_phrases_parts, message_texts, language_code="ru"):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    training_phrases = []
    for phrase in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent, "language_code": language_code}
    )
    print(f'Intent created: {response.display_name}')

def main():
    env = Env()
    env.read_env()
    project_id = env.str("DIALOGFLOW_PROJECT_ID")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")

    with open("questions.json", "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    for intent_name, value in questions_data.items():
        training_phrases = value["questions"]
        answer = value["answer"]
        create_intent(
            project_id=project_id,
            display_name=intent_name,
            training_phrases_parts=training_phrases,
            message_texts=[answer],
            language_code="ru"
        )

if __name__ == "__main__":
    main()
