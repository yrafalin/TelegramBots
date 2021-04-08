#!/usr/bin/env python3
import logging

from telegram.ext import Updater, CommandHandler, Filters, Defaults, PicklePersistence

from config import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


start = 'The count has been set to 0\nRaise it with /count [number]'
help = 'Raise the count with /count, /ct, or /c and a number'
eggs = {69:'\nnice ;)', 420:'\ngo green my dudes', 42: '\nthe answer to the ultimate question of life, the universe, and everything', 100:'\nnow we\'re getting somewhere!', 1000:'\nplease go do your work'}
num_list = '0123456789+-*/%^.()&|<>'


def send_start(update, context):
    chat_id = update.message.chat_id
    print('in start')

    if 'count' not in context.chat_data:
        context.chat_data['count'] = 0
        context.chat_data['stats'] = {}

    context.bot.send_message(chat_id=chat_id, text=start,
                             parse_mode='Markdown')


def send_help(update, context):
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=help,
                             parse_mode='Markdown')


def send_count(update, context):
    chat_id = update.message.chat_id
    sender = update.message.from_user['id']
    print('in count')

    if len(context.args) > 0:

        number = clean_number(''.join(context.args))
        print(number, sender)

        if number == '':
            message = 'That is not a number'
            context.bot.send_message(chat_id=chat_id, text=message,
                                     parse_mode='Markdown')
            return

        number = int(eval(number))

        if 'count' in context.chat_data:
            if number == context.chat_data['count']+1 and ('sender' not in context.chat_data or context.chat_data['sender'] != sender):
                context.chat_data['count'] = number
                context.chat_data['sender'] = sender
                update_stats(update, context, number, True)
                if number % 10 == 0 or number in eggs:
                    message = f"The count is {number}"
                    if number in eggs:
                        message = message + eggs[number]
                    context.bot.send_message(chat_id=chat_id, text=message,
                                             parse_mode='Markdown')
            else:
                context.chat_data['count'] = 0
                context.chat_data['sender'] = 0
                update_stats(update, context, number, False)
                message = 'The count is reset to 0'
                context.bot.send_message(chat_id=chat_id, text=message,
                                         parse_mode='Markdown')
        else:
            if number == 1:
                context.chat_data['count'] = 1
                context.chat_data['stats'] = {}
                context.chat_data['sender'] = sender
                message = f"The count is {number}"
                context.bot.send_message(chat_id=chat_id, text=message,
                                         parse_mode='Markdown')
            else:
                context.chat_data['count'] = 0
                context.chat_data['stats'] = {}
                message = 'The count has been set to 0'
                context.bot.send_message(chat_id=chat_id, text=message,
                                         parse_mode='Markdown')


def send_stats(update, context):
    chat_id = update.message.chat_id
    print('in stats')

    highscore = max(list(int(context.chat_data['stats'][user_id]['highscore']) for user_id in context.chat_data['stats'].keys()))
    successes = sum(list(int(context.chat_data['stats'][user_id]['successes']) for user_id in context.chat_data['stats'].keys()))
    failures = sum(list(int(context.chat_data['stats'][user_id]['failures']) for user_id in context.chat_data['stats'].keys()))
    personal_stats = []
    for user_id in context.chat_data['stats']:
        user_name = context.chat_data["stats"][user_id]["username"]
        user_score = context.chat_data["stats"][user_id]["highscore"]
        user_success = context.chat_data["stats"][user_id]["successes"]
        user_fail = context.chat_data["stats"][user_id]["failures"]
        personal_stats.append(f'\n\n*@ {user_name}*\nHigh score: {user_score}\nSuccesses: {user_success}\nFailures: {user_fail}')
    personal_stats = ''.join(personal_stats)

    message = f"*Overall stats*\nHigh score: {highscore}\nTotal successes: {successes}\nTotal failures: {failures}{personal_stats}"
    context.bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')


def clean_number(numstr):
    result = ''.join(filter(lambda x: x in num_list, numstr))
    result = result.lstrip('+*/%^.)')
    result = result.rstrip('+-*/%^.(')
    return result


def update_stats(update, context, number, success):
    user_id = str(update.message.from_user['id'])
    username = update.message.from_user['username']
    print('in update')

    if number != 1:
        if user_id not in context.chat_data['stats']:
            context.chat_data['stats'][user_id] = {'highscore': 0, 'successes': 0, 'failures': 0, 'username': username}

        if username != context.chat_data['stats'][user_id]['username']:
            context.chat_data['stats'][user_id]['username'] = username

        if success:
            if number > context.chat_data['stats'][user_id]['highscore']:
                context.chat_data['stats'][user_id]['highscore'] = number
            context.chat_data['stats'][user_id]['successes'] += 1
        else:
            context.chat_data['stats'][user_id]['failures'] += 1


def main():
    defaults = Defaults(disable_web_page_preview=True)
    pp = PicklePersistence(filename='chat_data_states', store_user_data=False,
                                 store_bot_data=False)

    updater = Updater(BOT_TOKEN, use_context=True, persistence=pp, defaults=defaults)

    dp = updater.dispatcher
    print('f')

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("help", send_help))
    dp.add_handler(CommandHandler(["count", "ct", "c"], send_count))
    dp.add_handler(CommandHandler(["stats", "getstats"], send_stats))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
