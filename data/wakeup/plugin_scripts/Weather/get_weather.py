#!/usr/bin/env python
# get weather for Weather
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import re
import pywapi, urllib2
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
    place = manual_location
    #weather = pywapi.get_weather_from_yahoo(manual_location)
else:
    # Get location
    sys.path.append('/usr/share/wakeup')
    import location
    loc = location.get_location()
    place = place = loc['City'] + ',' + loc['State'] + ',' + re.search('(.*?)\(',loc['Country']).group(1)
url = 'http://xoap.weather.com/search/search?where=' + place
req = urllib2.Request(url)
response = urllib2.urlopen(req,'',5)
page = response.read()
yahooid=re.search('loc id="(.*?)"',page).group(1)

# Get weather
weather = pywapi.get_weather_from_yahoo(yahooid,units='')



# Output the weather
for out in sys.argv[2:len(sys.argv)]:
    if (out == "temperature"):
        temperature = weather['condition']['temp']
        if temp_unit == "C":
            print '%g \n' %round(5.0/9*(float(temperature)-32))
        else:
            print temperature + '\n'
    if (out == "skyconditions"):
        print weather['condition']['text'] + '\n'
    if (out == "humidity"):
        humidity = weather['atmosphere']['humidity']
        if humidity == "":
            humidity = 'unknown'
        print humidity + '\n'
    if (out == "windconditions"):
        magnitude = weather['wind']['speed']
        direction = weather['wind']['direction']
        directions = ['north', 'north east', 'east', 'south east', 'south', 'south west', 'west', 'north west']
        maxdirs = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]
        directiontext='north'
        for i in range(1,len(directions)):
            if int(direction) > maxdirs[i-1] and int(direction) <= maxdirs[i]:
                directiontext=directions[i]
        if wind_unit == "knots":
            magnitude = int(round(float(magnitude) * 0.868976242))
        print directiontext + " at " + str(magnitude) + " " + wind_unit + '\n'
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
        print weather['forecasts'][0]['text'] + '\n'
