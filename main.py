import os
import time

import requests
import logging
import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google.cloud import dialogflow
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


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    update.message.reply_text(
        detect_intent_texts('dvmn-speech-recognizer', user_id, update.message.text)
    )


def main():
    load_dotenv()
    telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
    telegram_admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger_bot = telegram.Bot(token=telegram_api_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(logger_bot, telegram_admin_chat_id))

    updater = Updater(telegram_api_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    while True:
        try:
            updater.start_polling()
            updater.idle()
            logger.info('Бот запущен.')
        except requests.exceptions.ConnectionError:
            logger.error('Интернет исчез')
            time.sleep(5)
        except Exception as err:
            logger.error(f'Бот упал с ошибкой: {err}', exc_info=True)


if __name__ == '__main__':
    main()
