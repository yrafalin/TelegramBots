import logging

from telegram.ext import Updater, CommandHandler, Filters, Defaults, PicklePersistence

from config import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


start = 'The count has been set to 0\nRaise it with /count [number]'
help = 'Raise the count with /count, /ct, or /c and a number'


def send_start(update, context):
    chat_id = update.message.chat_id

    if 'count' not in context.chat_data:
        context.chat_data['count'] = 0

    context.bot.send_message(chat_id=chat_id, text=start,
                             parse_mode='Markdown')


def send_help(update, context):
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=help,
                             parse_mode='Markdown')


def send_count(update, context):
    chat_id = update.message.chat_id

    if 'count' in context.chat_data:
        if int(context.args[0]) == context.chat_data['count']+1:
            context.chat_data['count'] += 1
            message = f"The count is {context.args[0]}"
            context.bot.send_message(chat_id=chat_id, text=message,
                                     parse_mode='Markdown')
        else:
            context.chat_data['count'] = 0
            message = 'The count is reset to 0'
            context.bot.send_message(chat_id=chat_id, text=message,
                                     parse_mode='Markdown')
    else:
        if context.args[0] == '1':
            context.chat_data['count'] = 1
            message = f"The count is {context.args[0]}"
            context.bot.send_message(chat_id=chat_id, text=message,
                                     parse_mode='Markdown')
        else:
            context.chat_data['count'] = 0
            message = 'The count has been set to 0'
            context.bot.send_message(chat_id=chat_id, text=message,
                                     parse_mode='Markdown')


def main():
    defaults = Defaults(disable_web_page_preview=True)
    pp = PicklePersistence(filename='chat_data_states', store_user_data=False,
                                 store_bot_data=False)

    updater = Updater(BOT_TOKEN, use_context=True, persistence=pp, defaults=defaults)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("help", send_help))
    dp.add_handler(CommandHandler(["count", "ct", "c"], send_count))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
