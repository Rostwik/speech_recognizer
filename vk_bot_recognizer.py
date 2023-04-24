import os

import logging
import random
import time

import requests

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
import telegram
from dotenv import load_dotenv

from dialogflow_google_api import detect_intent_texts
from logger_handler import TelegramLogsHandler

logger = logging.getLogger('speech_recognizer')


def main():
    load_dotenv()
    vk_api_token = os.getenv('VK_API_TOKEN')
    telegram_admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    telegram_monitor_api_token = os.getenv('TELEGRAM_MONITOR_API_TOKEN')
    google_project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger_bot = telegram.Bot(token=telegram_monitor_api_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(logger_bot, telegram_admin_chat_id))

    vk_session = vk.VkApi(token=vk_api_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    while True:
        try:
            logger.info('VK Бот запущен.')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    response = detect_intent_texts(google_project_id, event.user_id, event.text)
                    if not response.query_result.intent.is_fallback:
                        vk_api.messages.send(
                            user_id=event.user_id,
                            message=response.query_result.fulfillment_text,
                            random_id=random.randint(1, 1000)
                        )
        except requests.exceptions.ConnectionError:
            logger.error('Интернет исчез')
            time.sleep(5)
        except Exception as err:
            logger.error(f'VK Бот упал с ошибкой: {err}', exc_info=True)


if __name__ == '__main__':
    main()
