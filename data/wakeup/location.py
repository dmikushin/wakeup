#!/usr/bin/env python
# get location for Weather
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

# Note this function can be imported, and gives a dictionary output of location data
# as available from the source www.ip-address.org. Data available may depend on location,
# but should include: 'City', 'State', 'Country', 'Continent', 'Time zone', 'City Lat/Lon',
# 'Country Lat/Lon', 'Continent Lat/Lon', 'My IP Address', 'My IP Host', 'ISP', 'Postal',
# and others.
# Some data about the computer, such as Browser, is useless but left for completion.
# Additionally, the dict keys 'longitude' and 'latitude' are added for ease of use; they
# are just taken from key 'City Lat/Lon'.

import urllib2
import re

def get_location():
    # Grab information about location based on IP
    url = 'http://www.ip-address.org'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req,'',5)
    page = response.read()
    tables = re.findall("<table.*?</table>", page,flags=re.DOTALL) # find tables
    table = tables[1] # get the right table
    table = re.sub(r"<th>([^<]*)<td",r"<th>\1</th><td",table) # fix missing end </th> tags
    table = re.sub("<br />", ";", table)
    tableelements = re.findall("<tr>.*?</tr>", table, flags=re.DOTALL)
    properties = {}
    for el in tableelements:
        try: # Get rid of leading junk, which may contain a <td> tag
            el = re.search('<th>.*', el, re.DOTALL).group(0)
        except:
            continue
        prop = re.search("<th>(.*):\s*</th>", el, flags=re.DOTALL)
        val = re.search("<td[^<]*>(.*)</td>", el, flags=re.DOTALL)
        if val: # skip if no value for this property (ie, it is just a header)
            properties[prop.group(1).strip()] = re.sub("<.*>|&nbsp;", "", val.group(1).strip())
    # Add latitude and longitude keys for direct ease of use
    [properties['latitude'],properties['longitude']] = \
                            re.findall("[0-9\.\-]+", properties['City Lat/Lon'])
    return properties
