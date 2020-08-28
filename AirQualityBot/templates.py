messages = {
    'search_failed_msg': 'Oops! Looks like that city couldn\'t be found.',
    'search_missing_msg': 'Hmmm, you might be missing a city name. Try again.',
    'home_request_msg': 'Are you sure you want to set this as your home location?',
    'here_request_msg': 'Would you mind sharing your location?',
    'home_set_msg': 'Your home location is all set! Now you can use /home and monitoring.',
    'missing_home_msg': 'Uhh oh! Your home location isn\'t set, use /sethome to set it.',
    'missing_time_msg': 'Hold on! You forgot to specify a valid 24 hour time for when to send the AQI update.',
    'monitor_success_msg': 'Monitoring has successfully been set. Way to go!',
    'monitor_off_msg': 'Monitoring has been turned off.',
    'missing_monitor_msg': 'Whoops, monitoring hasn\'t been turned on yet.',
    'home_canceled_msg': 'Looks like you didn\'t send a location. If privacy is a concern, use /search.',
    'bad_address_msg': 'Uhh oh! I couldn\'t read that zip code. Send only a 5 digit number.'
}

start = '''This bot helps you find pollution levels around the world with /search,
    at home with /home, and where you're at with /here. Get daily pollution updates
    with /monitoron and find more commands with /help.'''

help = '''📍To check the AQI of your location\n
/here\n
Make sure to "Send your location" and permit location sharing\n
\n
📍To check the AQI of anywhere\n
/search San Francisco\n
Keep in mind that not all cities have AQI sensors\n
Aliases: /find, /city\n
\n
📍To check the AQI of your home\n
/home\n
Home must be set with /sethome prior\n
\n
📍To set your home location\n
/sethome\n
Make sure to "Send your location" and permit location sharing\n
Aliases: /set\n
\n
📍To turn on daily AQI updates of your home\n
/monitoron 21:30\n
Specify a valid 24 hour time for when to send the AQI update\n
Home must be set with /sethome prior\n
Aliases: /mon, /getupdates, /startupdates\n
\n
📍To turn off daily AQI updates\n
/monitoroff\n
Aliases: /moff, /stopupdates\n'''

warnings = {
    'g': '',
    'm': 'People with respiratory disease, such as asthma, should limit prolonged outdoor exertion.\n',
    'usg': 'People with respiratory disease, such as asthma, should limit prolonged outdoor exertion.\n',
    'u': 'Everyone should limit prolonged outdoor exertion.\n',
    'vu': 'Everyone should limit outdoor exertion.\n',
    'h': 'Everyone should avoid all outdoor exertion.\n'
}
