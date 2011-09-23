#!/bin/bash
# plugin script for HebrewCalendar outputting Hebrew date and/or events
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

plugin_file="/home/$1/.wakeup/$ALARM/plugins/HebrewCalendar/HebrewCalendar.config"
manual_location=$(sed -rn 's/manual_location\s*=\s*(.*)\s*/\1/p' $plugin_file)
lat=$(sed -rn 's/latitude\s*=\s*(.*)\s*/\1/p' $plugin_file)
long=$(sed -rn 's/longitude\s*=\s*(.*)\s*/\1/p' $plugin_file)
for i in ${*:2}; do
    if [[ $i == hebdate ]]; then
	    echo $(hebcal -Th); echo ""
    fi
    if [[ $i == hebcalevents ]]; then
        if [[ $manual_location == "false" ]]; then
            latln=$(wget -q -U DummyBrowser/1.0 -O - www.ip-adress.com/ip_tracer | grep GLatLng)
            lat=$(echo $latln | grep -oP "\([0-9\-\.]+" | sed 's/(//')
            long=$(echo $latln | grep -oP "[0-9\-\.]+\)" | sed 's/)//')
        fi
	    # put longitude and latitude in deg,min format. Hebcal requires that longitude sign is switched
	    lat=$(echo $lat | perl -ne '$lat = abs($_); $deg = int($lat); $min = int(60 * ($lat - $deg)); print "$deg,$min"')
	    long=$(echo $long | perl -ne '$long = abs($_); $deg = int($long); $min = int(60 * ($long - $deg)); $deg *= -1 if not /-/; print "$deg,$min"')
	    echo $(hebcal -Toc -l $lat -L $long | sed /^[0-9].*/d); echo ""
    fi
done
