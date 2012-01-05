#!/usr/bin/env python
# get weather for Weather
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import re
import pywapi
import sys, os

# Get unit preferences
plugin_file = open('/home/' + sys.argv[1] + '/.wakeup/' + os.environ['ALARM'] + '/plugins/Weather/Weather.config', 'r')
plugin_text = ''.join(plugin_file.readlines())
plugin_file.close()
temp_unit = re.search("temperature_units=(.*)", plugin_text).group(1)
wind_unit = re.search("wind_units=(.*)", plugin_text).group(1)
if (wind_unit == "mph"):
    wind_unit = "miles per hour"
manual_location = re.search("location=(.*)", plugin_text).group(1)

if (manual_location != 'none'):
    # Using manual location
    weather = pywapi.get_weather_from_google(manual_location)
else:
    # Get location
    sys.path.append('/usr/share/wakeup')
    import location
    loc = location.get_location()
    weather = pywapi.get_weather_from_google(loc['city']+','+loc['state']+','+loc['country'])


# Output the weather
for out in sys.argv[2:len(sys.argv)]:
    if (out == "temperature"):
        if temp_unit == "C":
            print weather['current_conditions']['temp_c'] + '\n'
        else:
            print weather['current_conditions']['temp_f'] + '\n'
    if (out == "skyconditions"):
        print weather['current_conditions']['condition'] + '\n'
    if (out == "humidity"):
        print re.sub("Humidity: ", "", weather['current_conditions']['humidity']) + '\n'
    if (out == "windconditions"):
        winds =   weather['current_conditions']['wind_condition']
        magnitude = re.search("at (.*) mph", winds).group(1)
        direction = re.search("Wind: (.*) at", winds).group(1)
        direction = re.sub("N", "north ", direction)
        direction = re.sub("E", "east ", direction)
        direction = re.sub("S", "south ", direction)
        direction = re.sub("W", "west ", direction)
        if wind_unit == "knots":
            magnitude = int(round(float(magnitude) * 0.868976242))
        print direction + " at " + str(magnitude) + " " + wind_unit + '\n'
    if (out == "high"):
        high =  int(weather['forecasts'][0]['high'])
        if temp_unit == "C":
            print str(int(round((high - 32)*5/9))) + '\n'
        else:
            print str(high) + '\n'
    if (out == "low"):
        low =  int(weather['forecasts'][0]['low'])
        if temp_unit == "C":
            print str(int(round((low - 32)*5/9))) + '\n'
        else:
            print str(low) + '\n'
    if (out == "todays_forecast"):
        print weather['forecasts'][0]['condition'] + '\n'
