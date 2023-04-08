import os

import logging
from google.cloud import dialogflow
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import telegram
from dotenv import load_dotenv

logger = logging.getLogger('speech_recognizer')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(project_id, session_id, text, language_code='ru-RU'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text




def main():
    load_dotenv()
    vk_api_token = os.getenv('VK_API_TOKEN')
    telegram_admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger_bot = telegram.Bot(token=telegram_api_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(logger_bot, telegram_admin_chat_id))

    vk_session = vk_api.VkApi(token=vk_api_token)

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            if event.to_me:
                print('Для меня от: ', event.user_id)
            else:
                print('От меня для: ', event.user_id)
            print('Текст:', event.text)


        # try:
        #
        #     logger.info('Бот запущен.')
        # except requests.exceptions.ConnectionError:
        #     logger.error('Интернет исчез')
        #     time.sleep(5)
        # except Exception as err:
        #     logger.error(f'Бот упал с ошибкой: {err}', exc_info=True)


if __name__ == '__main__':
    main()