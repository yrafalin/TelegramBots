import logging
import datetime
import requests

from telegram.ext import Updater, CommandHandler, KeyboardButton, ReplyKeyboardMarkup, Filters

from config import *
from templates import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def send_start(update, context):
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=start,
                             parse_mode='Markdown')


def send_help(update, context):
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=help,
                             parse_mode='Markdown')


def send_set_home(update, context):
    chat_id = update.message.chat_id
    location_keyboard = KeyboardButton(
        text="Send home location 📍🏠", request_location=True)
    cancel_button = KeyboardButton(text="Cancel")
    custom_keyboard = [[location_keyboard, cancel_button]]
    reply_markup = ReplyKeyboardMarkup(
        custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=chat_id, text=messages['home_request_msg'],
                             parse_mode='Markdown', reply_markup=reply_markup)


def send_home(update, context):
    chat_id = update.message.chat_id

    if 'lat' in context.chat_data:
        lat = context.chat_data['lat']
        lon = context.chat_data['lon']

        endpoint = 'https://api.waqi.info/feed/geo:{0};{1}/?token={2}'.format(
            lat, lon, AQI_TOKEN)

        result = requests.get(endpoint).json()

        aqi = result['data']['aqi']
        city = result['data']['city']['name']
        url = result['data']['city']['url']
        pol = result['data']['dominentpol']
        aqilevel, warning = classify(aqi)

        message = f"*🏠 {city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol}\n{warning}\nFor more info, click [here]({url})\n_Source:_ waqi.info"

        context.bot.send_message(chat_id=chat_id, text=message,
                                 parse_mode='Markdown')
    else:
        context.bot.send_message(chat_id=chat_id, text=messages['missing_home_msg'])


def send_here(update, context):
    chat_id = update.message.chat_id
    location_keyboard = KeyboardButton(
        text="Send your location 📍🌎", request_location=True)
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
            aqi = result['data']['aqi']
            city = result['data']['city']['name']
            url = result['data']['city']['url']
            pol = result['data']['dominentpol']
            aqilevel, warning = classify(aqi)

            message = f"*{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol}\n{warning}\nFor more info, click [here]({url})\n_Source:_ waqi.info"

            context.bot.send_message(chat_id=chat_id, text=message,
                                     parse_mode='Markdown')
        else:
            context.bot.send_message(chat_id=chat_id, text=messages['search_failed_msg'])


def send_monitor_on(update, context):
    chat_id = update.message.chat_id

    if 'lat' in context.chat_data:
        try:
            # args[0] should contain the time for the timer in seconds
            reminder_time = datetime.strptime(context.args[0], "%H:%M")

            # Add job to queue and stop current one if there is a timer already
            if 'job' in context.chat_data:
                old_job = context.chat_data['job']
                old_job.schedule_removal()
            new_job = context.job_queue.run_daily(send_home_monitor, reminder_time, context=chat_id)
            context.chat_data['job'] = new_job

            context.bot.send_message(chat_id=chat_id, text=messages['monitor_success_msg'])

        except ValueError:
            context.bot.send_message(chat_id=chat_id, text=messages['missing_time_msg'])

    else:
        context.bot.send_message(chat_id=chat_id, text=messages['missing_home_msg'])


def send_monitor_off(update, context):
    chat_id = update.message.chat_id

    if 'job' in context.chat_data:
        job = context.chat_data['job']
        job.schedule_removal()
        del context.chat_data['job']

        context.bot.send_message(chat_id=chat_id, text=messages['moniter_off_msg'])

    else:
        context.bot.send_message(chat_id=chat_id, text=messages['missing_moniter_msg'])


def home_location_sent(update, context):
    chat_id = update.message.chat_id

    context.chat_data['lat'] = update.message.location['latitude']
    context.chat_data['lon'] = update.message.location['longitude']

    context.bot.send_message(chat_id=chat_id, text=messages['home_set_msg'])


def here_location_sent(update, context):
    chat_id = update.message.chat_id
    lat = update.message.location['latitude']
    lon = update.message.location['longitude']

    endpoint = 'https://api.waqi.info/feed/geo:{0};{1}/?token={2}'.format(
        lat, lon, AQI_TOKEN)

    result = requests.get(endpoint).json()

    aqi = result['data']['aqi']
    city = result['data']['city']['name']
    url = result['data']['city']['url']
    pol = result['data']['dominentpol']
    aqilevel, warning = classify(aqi)

    message = f"📍 *{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol}\n{warning}\nFor more info, click [here]({url})\n_Source:_ waqi.info"

    context.bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')


def location_canceled(update, context):
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=messages['home_canceled_msg'])


def send_home_monitor(context):
    job = context.job
    lat = context.chat_data['lat']
    lon = context.chat_data['lon']

    endpoint = 'https://api.waqi.info/feed/geo:{0};{1}/?token={2}'.format(
        lat, lon, AQI_TOKEN)

    result = requests.get(endpoint).json()

    aqi = result['data']['aqi']
    city = result['data']['city']['name']
    url = result['data']['city']['url']
    pol = result['data']['dominentpol']
    aqilevel, warning = classify(aqi)

    message = f"*🏠 {city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol}\n{warning}\nFor more info, click [here]({url})\n_Source:_ waqi.info"

    context.bot.send_message(job.context, text=message,
                             parse_mode='Markdown')


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


def main():
    updater = Updater("TOKEN", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("help", send_help))
    dp.add_handler(CommandHandler(["monitoron", "mon", "getupdates", "startupdates"], send_monitor_on))
    dp.add_handler(CommandHandler(["monitoroff", "moff", "stopupdates"], send_monitor_off))
    dp.add_handler(CommandHandler(["sethome", "set"], send_set_home))
    dp.add_handler(CommandHandler("home", send_home))
    dp.add_handler(CommandHandler("here", send_here))
    dp.add_handler(CommandHandler(["search", "find", "city"], send_search))

    dp.add_handler(MessageHandler(Filters.text('Send home location 📍🏠'), home_location_sent))
    dp.add_handler(MessageHandler(Filters.text('Send your location 📍🌎'), here_location_sent))
    dp.add_handler(MessageHandler(Filters.text('Cancel'), location_canceled))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
