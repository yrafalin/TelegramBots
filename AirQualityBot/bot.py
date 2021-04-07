#!/usr/bin/env python3
import logging
from datetime import datetime

import requests
import pytz
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from uszipcode import SearchEngine
from timezonefinder import TimezoneFinder
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Defaults, PicklePersistence

from config import *
from templates import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent="airqualitymonitorbot")


class ChatContext:
    def __init__(self, id, data):
        self.chat_id = id
        self.chat_data = data


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

    if len(context.args) > 1:
        context.bot.send_message(chat_id=chat_id, text=messages['bad_address_msg'])
    elif len(context.args) == 1:
        zipcode = zip_geo(context.args[0])
        if zipcode[0] is None or zipcode[1] is None:
            context.bot.send_message(chat_id=chat_id, text=messages['bad_address_msg'])
            return
        context.chat_data['lat'] = zipcode[0]
        context.chat_data['lon'] = zipcode[1]
        print(context.chat_data['lat'], context.chat_data['lon'])

        aqi, city, url, pol = request_aqi_by_geo(zipcode[0], zipcode[1])
        context.chat_data['city'] = city

        context.bot.send_message(chat_id=chat_id, text=messages['home_set_msg'])
    else:
        location_keyboard = KeyboardButton(
            text="Send home location 📍🏠", request_location=True)
        cancel_button = KeyboardButton(text="Cancel")
        custom_keyboard = [[location_keyboard, cancel_button]]
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.chat_data['pending'] = 'home'
        context.bot.send_message(chat_id=chat_id, text=messages['home_request_msg'],
                                 parse_mode='Markdown', reply_markup=reply_markup)


def send_home(update, context):
    chat_id = update.message.chat_id

    if 'city' in context.chat_data:
        lat = context.chat_data['lat']
        lon = context.chat_data['lon']

        aqi, city, url, pol = request_aqi_by_geo(lat, lon)
        aqilevel, warning = classify(aqi)

        message = f"*🏠 {city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, click [here]({url})\n_Source:_ iqair.com"

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

    context.chat_data['pending'] = 'here'
    context.bot.send_message(chat_id=chat_id, text=messages['here_request_msg'],
                             parse_mode='Markdown', reply_markup=reply_markup)


def send_search(update, context):
    chat_id = update.message.chat_id

    if not context.args:
        context.bot.send_message(chat_id=chat_id, text=messages['search_missing_msg'])
    elif ' '.join(context.args).isdigit():
        zipcode = zip_geo(context.args[0])

        aqi, city, url, pol = request_aqi_by_geo(zipcode[0], zipcode[1])
        aqilevel, warning = classify(aqi)

        message = f"*{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, click [here]({url})\n_Source:_ iqair.com"

        context.bot.send_message(chat_id=chat_id, text=message,
                                 parse_mode='Markdown')
    else:
        try:
            location = geolocator.geocode(' '.join(context.args))
            print(location)

            if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                aqi, city, url, pol = request_aqi_by_geo(location.latitude, location.longitude)
                aqilevel, warning = classify(aqi)

                message = f"*{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, click [here]({url})\n_Source:_ iqair.com"

                context.bot.send_message(chat_id=chat_id, text=message,
                                         parse_mode='Markdown')
            else:
                context.bot.send_message(chat_id=chat_id, text=messages['search_failed_msg'])
        except GeocoderUnavailable:
            context.bot.send_message(chat_id=chat_id, text=messages['geo_unavailable_msg'])


def send_monitor_on(update, context):
    chat_id = update.message.chat_id

    if len(context.args) != 1:
        context.bot.send_message(chat_id=chat_id, text=messages['missing_time_msg'])
        return

    if 'city' in context.chat_data:
        try:
            tf = TimezoneFinder()
            tz_at_home = tf.timezone_at(lng=context.chat_data['lon'], lat=context.chat_data['lat'])
            hometz = pytz.timezone(tz_at_home)
            print(hometz)

            reminder_time = datetime.utcnow()
            # args[0] should contain the time for the timer in seconds
            input_time = datetime.strptime(context.args[0], "%H:%M")
            print(input_time)
            reminder_time = reminder_time.replace(hour=input_time.hour, minute=input_time.minute, second=input_time.minute)
            print(reminder_time)
            reminder_time = (reminder_time - hometz.utcoffset(reminder_time)).time()
            print(reminder_time)

            # Add job to queue and stop current one if there is one already
            if 'job' in context.chat_data:
                old_job = context.bot_data[chat_id]
                old_job.schedule_removal()

            context.chat_data['time'] = context.args[0]
            job_context = ChatContext(chat_id, context.chat_data)
            new_job = context.job_queue.run_daily(send_home_monitor, reminder_time, context=job_context)
            context.bot_data[chat_id] = new_job
            context.chat_data['job'] = True

            context.bot.send_message(chat_id=chat_id, text=messages['monitor_success_msg'])

        except ValueError:
            context.bot.send_message(chat_id=chat_id, text=messages['missing_time_msg'])

    else:
        context.bot.send_message(chat_id=chat_id, text=messages['missing_home_msg'])


def send_monitor_off(update, context):
    chat_id = update.message.chat_id

    if 'job' in context.chat_data:
        job = context.bot_data[chat_id]
        job.schedule_removal()
        del context.bot_data[chat_id]
        del context.chat_data['job']

        context.bot.send_message(chat_id=chat_id, text=messages['monitor_off_msg'])

    else:
        context.bot.send_message(chat_id=chat_id, text=messages['missing_monitor_msg'])


def send_monitor_status(update, context):
    chat_id = update.message.chat_id

    if 'job' in context.chat_data:
        message = f"The monitor is currently on, set for {context.chat_data['time']}. To turn it off, enter /monitoroff.\n\nYour home is set as *{context.chat_data['city']}*. You can change it with /sethome."
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    else:
        if 'city' in context.chat_data:
            message = f"The monitor is currently off. To turn it on, enter /monitoron and a time.\n\nYour home is set as *{context.chat_data['city']}*. You can change it with /sethome."
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            context.bot.send_message(chat_id=chat_id, text=messages['status_off_msg'])


def location_sent(update, context):
    if 'pending' in context.chat_data:
        if context.chat_data['pending'] == 'home':
            home_location_sent(update, context)
        elif context.chat_data['pending'] == 'here':
            here_location_sent(update, context)


def home_location_sent(update, context):
    chat_id = update.message.chat_id

    lat = update.message.location['latitude']
    lon = update.message.location['longitude']

    context.chat_data['lat'] = lat
    context.chat_data['lon'] = lon
    print(context.chat_data['lat'], context.chat_data['lon'])

    aqi, city, url, pol = request_aqi_by_geo(lat, lon)
    context.chat_data['city'] = city

    context.chat_data['pending'] = None
    context.bot.send_message(chat_id=chat_id, text=messages['home_set_msg'])


def here_location_sent(update, context):
    chat_id = update.message.chat_id
    lat = update.message.location['latitude']
    lon = update.message.location['longitude']

    aqi, city, url, pol = request_aqi_by_geo(lat, lon)
    aqilevel, warning = classify(aqi)

    message = f"📍 *{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, click [here]({url})\n_Source:_ iqair.com"

    context.chat_data['pending'] = None
    context.bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')


def location_canceled(update, context):
    chat_id = update.message.chat_id

    if 'pending' in context.chat_data and context.chat_data['pending']:
        context.bot.send_message(chat_id=chat_id, text=messages['home_canceled_msg'])


def send_home_monitor(context):
    job = context.job
    lat = job.context.chat_data['lat']
    lon = job.context.chat_data['lon']
    print('SENDING DAILY UPDATE', job.context.chat_data)

    aqi, city, url, pol = request_aqi_by_geo(lat, lon)
    aqilevel, warning = classify(aqi)

    message = f"{job.context.chat_data['time']} *Your daily update!*\n*🏠 {city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, click [here]({url})\n_Source:_ iqair.com"

    context.bot.send_message(job.context.chat_id, text=message,
                             parse_mode='Markdown')


def restart_jobs(dp):
    for chat_id in dp.chat_data:
        if 'job' in dp.chat_data[chat_id]:
            tf = TimezoneFinder()
            tz_at_home = tf.timezone_at(lng=dp.chat_data[chat_id]['lon'], lat=dp.chat_data[chat_id]['lat'])
            hometz = pytz.timezone(tz_at_home)

            reminder_time = datetime.utcnow()
            input_time = datetime.strptime(dp.chat_data[chat_id]['time'], "%H:%M")
            reminder_time = reminder_time.replace(hour=input_time.hour, minute=input_time.minute, second=input_time.minute)
            reminder_time = (reminder_time - hometz.utcoffset(reminder_time)).time()

            job_context = ChatContext(chat_id, dp.chat_data[chat_id])
            new_job = dp.job_queue.run_daily(send_home_monitor, reminder_time, context=job_context)
            dp.bot_data[chat_id] = new_job


def zip_geo(zip):
    search = SearchEngine()
    zipcode = search.by_zipcode(zip).to_dict()
    return [zipcode['lat'], zipcode['lng']]


def request_aqi_by_geo(lat, lon):
    endpoint = 'http://api.airvisual.com/v2/nearest_city?lat={0}&lon={1}&key={2}'.format(
        lat, lon, AQI_TOKEN)

    result = requests.get(endpoint).json()

    aqi = result['data']['current']['pollution']['aqius']
    city = ', '.join((result['data']['city'],result['data']['state'],result['data']['country']))
    pol = pol_names[result['data']['current']['pollution']['mainus']]

    address = [result['data']['country'],result['data']['state'],result['data']['city']]
    if 'station' in result['data']:
        address.append(result['data']['station'])
    address = map(lambda point: point.lower().replace(' ', '-'), address)
    url = 'iqair.com/us/'+'/'.join(address)

    print(datetime.now(), aqi, city, url, pol)

    return aqi, city, url, pol


def classify(straqi):
    aqi = int(straqi)
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


# def print_id(update, context):
#     print(update.message.message_id, update.message.text[:10], update.message.from_user)


def main():
    defaults = Defaults(disable_web_page_preview=True)
    pp = PicklePersistence(filename='chat_data_states', store_user_data=False,
                                 store_bot_data=False)

    updater = Updater(BOT_TOKEN, use_context=True, persistence=pp, defaults=defaults)

    dp = updater.dispatcher

    restart_jobs(dp)

    dp.add_handler(CommandHandler("start", send_start))
    dp.add_handler(CommandHandler("help", send_help))
    dp.add_handler(CommandHandler(["monitoron", "mon", "getupdates", "startupdates"], send_monitor_on))
    dp.add_handler(CommandHandler(["monitoroff", "moff", "stopupdates"], send_monitor_off))
    dp.add_handler(CommandHandler(["monitorstatus", "mstatus", "status"], send_monitor_status))
    dp.add_handler(CommandHandler(["sethome", "set"], send_set_home))
    dp.add_handler(CommandHandler("home", send_home))
    dp.add_handler(CommandHandler("here", send_here))
    dp.add_handler(CommandHandler(["search", "find", "city"], send_search))

    dp.add_handler(MessageHandler(Filters.location, location_sent))
    dp.add_handler(MessageHandler(Filters.regex(r'Cancel'), location_canceled))
    # dp.add_handler(MessageHandler(Filters.text, print_id))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
