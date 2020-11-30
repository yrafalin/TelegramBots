import logging
import random
import csv
import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence

from config import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def send_start(update, context):
    chat_id = update.message.chat_id
    context.chat_data['login'] = 0
    print('starting')


def check_assassin(update, context):
    chat_id = update.message.chat_id
    if 'login' not in context.chat_data:
        context.chat_data['login'] = 0
    if context.chat_data['login'] == 0:
        context.bot.send_message(chat_id=chat_id, text='Sorry, I don\'t know your name. Use /set [name].')
        return
    if context.chat_data['login'] == 1:
        context.bot.send_message(chat_id=chat_id, text='Please enter a password with /login [password] before continuing.')
        return
    guess = update.message.text
    if num_past_week(context.chat_data['attempts']) < 2:
        with open(PAIRINGS, 'r') as csvfile:
            pairings_reader = list(csv.reader(csvfile))
        idx = [row[0] for row in pairings_reader].index(context.chat_data['name'])
        if pairings_reader[idx][3] == guess:
            context.chat_data['attempts'].append(datetime.datetime.now())
            context.bot.send_message(chat_id=chat_id, text='You are correct!')
        else:
            context.chat_data['attempts'].append(datetime.datetime.now())
            context.bot.send_message(chat_id=chat_id, text='Sorry, you\'re incorrect. An attempt has been logged.')
    else:
        context.bot.send_message(chat_id=chat_id, text='Sorry, you\'ve already had 2 attempts in the past week.')


def num_past_week(attempts):
    count = 0
    for x in attempts:
        if x > datetime.datetime.now() - datetime.timedelta(days=7):
            count += 1
    return count


def set_name(update, context):
    chat_id = update.message.chat_id
    if 'login' not in context.chat_data:
        context.chat_data['login'] = 0
    if len(context.args) == 1:
        context.bot.send_message(chat_id=chat_id, text='Sorry, but that is not a participant\'s name.')
        return
    name = ' '.join(context.args)
    if 'name' not in context.chat_data:
        if check_name(name):
            context.chat_data['name'] = name
            context.chat_data['login'] = 1
            context.bot.send_message(chat_id=chat_id, text='Please send the correct password with /login [password].')
        else:
            context.bot.send_message(chat_id=chat_id, text='Sorry, but that is not a participant\'s name. Put the first name and last initial.')
    else:
        context.bot.send_message(chat_id=chat_id, text='Sorry, but you already have a name. To change it please contact Andrew.')


def set_login(update, context):
    chat_id = update.message.chat_id
    if 'login' not in context.chat_data:
        context.chat_data['login'] = 0
    if len(context.args) < 1 or len(context.args) > 1:
        context.bot.send_message(chat_id=chat_id, text='Sorry, that is not a valid password. Please enter just one word.')
        return
    pwd = ' '.join(context.args)
    if context.chat_data['login'] == 0:
        context.bot.send_message(chat_id=chat_id, text='Please set your name with /set [name] before entering a password.')
    elif context.chat_data['login'] == 2:
        context.bot.send_message(chat_id=chat_id, text='Whoops, you\'re already fully logged in.')
    elif context.chat_data['login'] == 1:
        with open(PAIRINGS, 'r') as csvfile:
            pairings_reader = list(csv.reader(csvfile))
        idx = [row[0] for row in pairings_reader].index(context.chat_data['name'])
        if pairings_reader[idx][1] == pwd:
            context.chat_data['attempts'] = []
            context.chat_data['login'] = 2
            context.bot.send_message(chat_id=chat_id, text='Your name has been set. You can now guess your assassin!')
        else:
            del context.chat_data['name']
            context.chat_data['login'] = 0
            context.bot.send_message(chat_id=chat_id, text='Sorry, that password is incorrect. Please start over.')


def check_name(name):
    with open(PAIRINGS, 'r') as csvfile:
        pairings_reader = csv.reader(csvfile)
        return name in [row[0] for row in pairings_reader][1:]


def main():
    pp = PicklePersistence(filename='chat_data_states', store_user_data=False,
                                 store_bot_data=False)

    updater = Updater(BOT_TOKEN, use_context=True, persistence=pp)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("set", set_name))
    dp.add_handler(CommandHandler("login", set_login))
    dp.add_handler(MessageHandler(Filters.text, check_assassin))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
