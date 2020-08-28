import logging
import requests

from telegram.ext import Updater, CommandHandler, KeyboardButton, ReplyKeyboardMarkup, Filters

from config import *
from templates import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def send_set_home(update, context):
    chat_id = update.message.chat_id
    location_keyboard = KeyboardButton(
        text="Send home location", request_location=True)
    cancel_button = KeyboardButton(text="Cancel")
    custom_keyboard = [[location_keyboard, cancel_button]]
    reply_markup = ReplyKeyboardMarkup(
        custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=chat_id, text=messages['home_request_msg'],
                             parse_mode='Markdown', reply_markup=reply_markup)


def send_home(update, context):
    chat_id = update.message.chat_id


def send_here(update, context):
    chat_id = update.message.chat_id
    location_keyboard = KeyboardButton(
        text="Send location", request_location=True)
    cancel_button = KeyboardButton(text="Cancel")
    custom_keyboard = [[location_keyboard, cancel_button]]
    reply_markup = ReplyKeyboardMarkup(
        custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=chat_id, text=messages['here_request_msg'],
                             parse_mode='Markdown', reply_markup=reply_markup)


def send_search(update, context):
    chat_id = update.message.chat_id

    if not context.args:
        context.bot.send_message(chat_id=chat_id, text=messages['search_missing_msg'])
    else:
        endpoint = f"https://api.waqi.info/search/?keyword={' '.join(args)}&token={AQI_TOKEN}"

        result = requests.get(endpoint).json()

        if result['status'] == 'ok' and len(result['data']) > 0:

        else:
            context.bot.send_message(chat_id=chat_id, text=messages['search_failed_msg'])


def send_start_updates(update, context):
    chat_id = update.message.chat_id


def send_stop_updates(update, context):
    chat_id = update.message.chat_id


def home_location_sent(update, context):
    chat_id = update.message.chat_id
    context.chat_data['lat'] = lat
    context.chat_data['lon'] = lon


def here_location_sent(update, context):
    chat_id = update.message.chat_id
    lat = update.message.location['latitude']
    lon = update.message.location['longitude']

    endpoint = 'https://api.waqi.info/feed/geo:{0};{1}/?token={2}'.format(
        lat, lon, AQI_TOKEN)

    result = requests.get(endpoint).json()

    message =

    context.bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')



def location_canceled(update, context):
    chat_id = update.message.chat_id


def classify(aqi):
    if aqi < 51:
        return "Good", warnings['g']
    elif aqi < 101:
        return "Moderate", warnings['m']
    elif aqi < 151:
        return "Unhealthy for Sensitive Groups", warnings['usg']
    elif aqi < 201:
        return "Unhealthy", warnings['u']
    elif aqi < 301:
        return "Very Unhealthy", warnings['vu']
    else:
        return "Hazardous", warnings['h']


def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def main():
    updater = Updater("TOKEN", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("help", send_start))
    dp.add_handler(CommandHandler("getupdates", send_start_updates))
    dp.add_handler(CommandHandler("stopupdates", send_stop_updates))
    dp.add_handler(CommandHandler("sethome", send_set_home))
    dp.add_handler(CommandHandler("home", send_home))
    dp.add_handler(CommandHandler("here", send_here))
    dp.add_handler(CommandHandler("search", send_search))

    dp.add_handler(MessageHandler(Filters.text('Send home location'), home_location_sent))
    dp.add_handler(MessageHandler(Filters.text('Send location'), here_location_sent))
    dp.add_handler(MessageHandler(Filters.text('Cancel'), location_canceled))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
