import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from config import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def send_start(update, context):
    chat_id = update.message.chat_id
    context.chat_data['active'] = True
    context.bot.send_message(chat_id=chat_id, text=start)


def send_pause(update, context):
    chat_id = update.message.chat_id
    context.chat_data['active'] = False
    context.bot.send_message(chat_id=chat_id, text="Paused")


def send_resume(update, context):
    chat_id = update.message.chat_id
    context.chat_data['active'] = True
    context.bot.send_message(chat_id=chat_id, text="Resumed")


def send_sticker_spam(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if context.chat_data['active']:
        context.bot.send_sticker(chat_id=chat_id, sticker=STICKER_SPAM, disable_notification=True, reply_to_message_id=message_id)


def main():
    pp = PicklePersistence(filename='chat_data_states', store_user_data=False,
                                 store_bot_data=False)

    updater = Updater(BOT_TOKEN, use_context=True, persistence=pp)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("pause", send_pause))
    dp.add_handler(CommandHandler("resume", send_resume))
    dp.add_handler(MessageHandler(Filters.user(TARGET), send_sticker_spam))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
