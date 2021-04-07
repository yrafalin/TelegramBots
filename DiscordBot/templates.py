messages = {
    'search_failed_msg': 'Oops! Looks like that location couldn\'t be found.',
    'search_missing_msg': 'Hmmm, you might be missing a city name. Try again.',
    'home_set_msg': 'Your home location is all set! Now you can use aqi:home.',
    'missing_home_msg': 'Uhh oh! Your home location isn\'t set, use aqi:set to set it.',
    'bad_address_msg': 'Uhh oh! I couldn\'t read that zip code. Send only a 5 digit number.',
    'geo_unavailable_msg': 'Unfortunately our location search is unavailable at the moment.',
    'invalid_msg': 'Sorry, that is an invalid command. Please look to aqi:help.'
}

start = '''This bot helps you find pollution levels around the world with aqi:search, and at home with aqi:home. Set your home zip code with aqi:set.'''

help = '''📍To check the AQI of anywhere\naqi:search San Francisco\nKeep in mind that not all cities have AQI sensors\nAliases: aqi:find, aqi:city\n\n📍To check the AQI of your home\naqi:home\nHome must be set with aqi:set prior\n\n📍To set your home location by zip code\naqi:set 55555\nMake sure to send a valid American zip code'''
# ''' 📍To check the AQI of anywhere\n
# aqi:search San Francisco\n
# Keep in mind that not all cities have AQI sensors\n
# Aliases: aqi:find, aqi:city\n
# \n
# 📍To check the AQI of your home\n
# aqi:home\n
# Home must be set with aqi:set prior\n
# \n
# 📍To set your home location by zip code\n
# aqi:set 55555\n
# Make sure to send a valid American zip code'''

pol_names = {'p2': 'PM2.5', 'p1': 'PM10', 'o3': 'O3', 'n2': 'NO2', 's2': 'SO2', 'co': 'CO2'}

warnings = {
    'g': '',
    'm': 'People with respiratory disease, such as asthma, should limit prolonged outdoor exertion.\n',
    'usg': 'People with respiratory disease, such as asthma, should limit prolonged outdoor exertion.\n',
    'u': 'Everyone should limit prolonged outdoor exertion.\n',
    'vu': 'Everyone should limit outdoor exertion.\n',
    'h': 'Everyone should avoid all outdoor exertion.\n'
}
