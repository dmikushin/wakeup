#!/usr/bin/env python
# get hebcal data
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import re
import sys, os
from commands import getoutput


# Get preferences
plugin_file = open('/home/' + sys.argv[1] + '/.wakeup/' + os.environ['ALARM'] + '/plugins/HebrewCalendar/HebrewCalendar.config', 'r')
plugin_text = ''.join(plugin_file.readlines())
plugin_file.close()
latitude = re.search("latitude=(.*)", plugin_text).group(1)
longitude = re.search("longitude=(.*)", plugin_text).group(1)
manual_location = re.search("manual_location=(.*)", plugin_text).group(1)

# Output
for out in sys.argv[2:len(sys.argv)]:
    if (out == "hebdate"):
        date = getoutput('echo $(hebcal -Th)')
        print date + '\n'
    if (out == "hebcalevents"):
        if (manual_location == "false"):
            # Get location
            sys.path.append('/usr/share/wakeup')
            import location
            loc = location.get_location()
            latitude = loc['latitude']
            longitude = loc['longitude']
        # Convert to hebcal +/-deg,min
        lat_deg = int(abs(latitude))
        lat_min = int(60 * (abs(latitude) - lat_deg))
        lat_deg = int(latitude/abs(latitude)) * lat_deg
        lon_deg = int(abs(longitude))
        lon_min = int(60 * (abs(longitude) - lon_deg))
        lon_deg = -1 * int(longitude/abs(longitude)) * lon_deg
        latitude = str(lat_deg) + ',' + str(lat_min)
        longitude = str(lon_deg) + ',' + str(lon_min)
        events = getoutput('echo $(hebcal -Toc -l ' + latitude + ' -L ' + longitude + ' -z $(date +%:::z) | sed /^[0-9].*/d)')
        print events + '\n'
            
