#!/usr/bin/env python
# get location for Weather
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

# Note this function can be imported, and gives a dictionary output of location data
# as follows: {country_code, country, state, city, postcode, latitude, longitude}.
# If any of the values are not available, they default to an empty string ('').
# Data is taken from ip-address.org.

import urllib2
import re

def get_location():
    # Grab information about location based on IP
    url = 'http://www.ip-address.org'
    headers = {'User-Agent' : 'Dummy/0.0'}
    req = urllib2.Request(url, '', headers)
    response = urllib2.urlopen(req,'',5)
    page = response.read()
    data = re.search("Browser Language.*IP Language",page).group(0)
    try:
        country = re.search("Country:</th><td>(.*)&nbsp;&nbsp;", data).group(1)
    except:
        country = ''
    try:
        country_code = re.search("img src.*\((.*)\).*State:", data).group(1)
    except:
        country_code = ''
    try:
        state = re.search("State:</th><td class='lookup'>(.*)</td>.*City:", data).group(1)
    except:
        state = ''
    try:
        city = re.search("City:</th><td>(.*)</td>.*Postal:", data).group(1)
    except:
        city = ''
    try:
        postcode = re.search("Postal:.*'lookup'>(.*)</td>.*ISP:", data).group(1)
    except:
        postcode = ''
    try:
        latlon = re.search("City Lat/Lon:.*'lookup'> \((.*)\) / \((.*)\)</td>", data)
        latitude = latlon.group(1)
        longitude = latlon.group(2)
    except:
        longitude = ''
        longitude = ''

    return {'country_code':country_code, 'country':country, 'state':state, 'city':city, 'postcode':postcode, 'latitude':latitude, 'longitude':longitude}
