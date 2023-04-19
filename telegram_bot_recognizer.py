import os

import logging
import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

from dialogflow_google_api import detect_intent_texts, TelegramLogsHandler

logger = logging.getLogger('speech_recognizer')


def error_handler(update, context):
    logger.error(f'Телеграм бот упал с ошибкой: {context.error}', exc_info=True)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def send_intent_response(update: Update, context: CallbackContext, google_project_id):
    user_id = update.message.chat_id
    response = detect_intent_texts(google_project_id, user_id, update.message.text)
    update.message.reply_text(
        response.query_result.fulfillment_text
    )


def main():
    load_dotenv()
    telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
    telegram_monitor_api_token = os.getenv('TELEGRAM_MONITOR_API_TOKEN')
    telegram_admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    google_project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger_bot = telegram.Bot(token=telegram_monitor_api_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(logger_bot, telegram_admin_chat_id))

    updater = Updater(telegram_api_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        lambda update, context: send_intent_response(update, context, google_project_id))
    )
    dispatcher.add_error_handler(error_handler)

    logger.info('Телеграм бот запущен.')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
