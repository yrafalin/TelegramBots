import logging
import random
import string

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from config import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def send_start(update, context):
    chat_id = update.message.chat_id
    context.chat_data['active'] = True
    print('starting')
    #context.bot.send_message(chat_id=chat_id, text=start)


def send_pause(update, context):
    chat_id = update.message.chat_id
    context.chat_data['active'] = False
    context.bot.send_message(chat_id=chat_id, text="Paused")


def send_resume(update, context):
    chat_id = update.message.chat_id
    print(chat_id)
    context.chat_data['active'] = True
    context.bot.send_message(chat_id=chat_id, text="Resumed")


def send_sticker_spam(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if context.chat_data['active']:
        randnum = random.random()
        if randnum <= 0.03:
            context.bot.send_sticker(chat_id=chat_id, sticker=open(fileone, 'rb'), disable_notification=True, reply_to_message_id=message_id)
        elif randnum <= 0.033:
            context.bot.send_sticker(chat_id=chat_id, sticker=open(filetwo, 'rb'), disable_notification=True, reply_to_message_id=message_id)


def send_anonpoll(update, context):
    print('got a poll')
    print(vars(update))
    print(update.message.poll.question)
    context.bot.send_poll(chat_id=poll_group_id, question=update.message.poll.question, options=[x.text for x in update.message.poll.options], is_anonymous=update.message.poll.is_anonymous, allows_multiple_answers=update.message.poll.allows_multiple_answers)


def print_id(update, context):
    chat_id = update.message.chat_id
    clean_text = ''.join(ch for ch in update.message.text if ch.isalnum())
    if clean_text[-3:].lower() in ('two', 'too') or clean_text[-1:] == '2':
        context.bot.send_message(chat_id=chat_id, text="Electric boogaloo!")
    print(update.message.message_id, update.message.text[:10], update.message.from_user)


def main():
    pp = PicklePersistence(filename='chat_data_states', store_user_data=False,
                                 store_bot_data=False)

    updater = Updater(BOT_TOKEN, use_context=True, persistence=pp)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("pause", send_pause))
    dp.add_handler(CommandHandler("resume", send_resume))
    dp.add_handler(MessageHandler(Filters.poll, send_anonpoll))
    dp.add_handler(MessageHandler(Filters.user(TARGET), send_sticker_spam))
    dp.add_handler(MessageHandler(Filters.text, print_id))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()


# https://stackoverflow.com/questions/37189496/how-telegram-bot-can-get-file-id-of-uploaded-file
