import logging
from google.cloud import dialogflow_v2 as dialogflow

logger = logging.getLogger(__name__)

def detect_intent_text(text, user_id, project_id, language_code="ru"):
    """Запрашивает у DialogFlow ответ на текст, возвращает fulfillment_text."""
    try:
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, str(user_id))

        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        logger.info(
            f"DialogFlow: user_id={user_id}, text='{text}', intent='{response.query_result.intent.display_name}'"
        )
        return response.query_result.fulfillment_text
    except Exception as error:
        logger.error(f"DialogFlow error: {error}", exc_info=True)
        raise
