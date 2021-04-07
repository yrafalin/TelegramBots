#!/usr/bin/env python3
import logging
import json
from datetime import datetime

import discord
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from uszipcode import SearchEngine
from timezonefinder import TimezoneFinder

from config import *
from templates import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent="airqualitymonitorbot")


client = discord.Client()

@client.event
async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    msg = message.content
    chat_id = str(message.channel.id)
    if chat_id not in chat_data:
        chat_data[chat_id] = {}
    if msg.startswith('aqi:'):
        if msg.startswith('aqi:set '):
            msg_args = msg[8:].split()
            if len(msg_args) == 1 and msg_args[0].isnumeric():
                zipcode = zip_geo(msg_args[0])
                if zipcode[0] is None or zipcode[1] is None:
                    await message.channel.send(messages['bad_address_msg'])
                    return
                chat_data[chat_id]['lat'] = zipcode[0]
                chat_data[chat_id]['lon'] = zipcode[1]
                print(chat_data[chat_id]['lat'], chat_data[chat_id]['lon'])

                aqi, city, url, pol = request_aqi_by_geo(zipcode[0], zipcode[1])
                chat_data[chat_id]['city'] = city

                await message.channel.send(messages['home_set_msg'])
            else:
                await message.channel.send(messages['bad_address_msg'])

        elif msg.startswith('aqi:home'):
            if 'city' in chat_data[chat_id]:
                lat = chat_data[chat_id]['lat']
                lon = chat_data[chat_id]['lon']

                aqi, city, url, pol = request_aqi_by_geo(lat, lon)
                aqilevel, warning = classify(aqi)

                update = f"*🏠 {city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, go to http://{url}\n_Source:_ iqair.com"

                await message.channel.send(update)
            else:
                await message.channel.send(messages['missing_home_msg'])

        elif msg.startswith('aqi:search ') or msg.startswith('aqi:find ') or msg.startswith('aqi:city '):
            msg_args = msg[msg.index(' ')+1:].split()
            if len(msg_args) < 1:
                await message.channel.send(messages['search_missing_msg'])
            elif ' '.join(msg_args).isdigit():
                zipcode = zip_geo(msg_args[0])

                aqi, city, url, pol = request_aqi_by_geo(zipcode[0], zipcode[1])
                aqilevel, warning = classify(aqi)

                update = f"📍*{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, go to http://{url}\n_Source:_ iqair.com"

                await message.channel.send(update)
            else:
                try:
                    location = geolocator.geocode(' '.join(msg_args))
                    print(location)

                    if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                        aqi, city, url, pol = request_aqi_by_geo(location.latitude, location.longitude)
                        aqilevel, warning = classify(aqi)

                        update = f"*{city}*\nAQI: {aqi} ({aqilevel})\nDominant pollutant: {pol.upper()}\n{warning}\nFor more info, go to http://{url}\n_Source:_ iqair.com"

                        await message.channel.send(update)
                    else:
                        await message.channel.send(messages['search_failed_msg'])
                except GeocoderUnavailable:
                    await message.channel.send(messages['geo_unavailable_msg'])

        elif msg.startswith('aqi:help'):
            await message.channel.send(help)
        else:
            await message.channel.send(messages['invalid_msg'])


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
        return "Good 🟩", warnings['g']
    elif aqi < 101:
        return "Moderate 🟨", warnings['m']
    elif aqi < 151:
        return "Unhealthy for Sensitive Groups 🟧", warnings['usg']
    elif aqi < 201:
        return "Unhealthy 🟥", warnings['u']
    elif aqi < 301:
        return "Very Unhealthy 🟪", warnings['vu']
    else:
        return "Hazardous 🟫", warnings['h']


def save_chat_data():
    with open(filename, "w") as data_file:
        json.dump(chat_data, data_file, indent=4)



with open(filename) as data_file:
    chat_data = json.load(data_file)
    print(chat_data)
    # chat_data = { [channel_id]: {'lat': [lat], 'lon': [lon], 'city': [city]}, ... }

try:
    client.run(BOT_TOKEN)
except BaseException:
    pass
finally:
    save_chat_data()
