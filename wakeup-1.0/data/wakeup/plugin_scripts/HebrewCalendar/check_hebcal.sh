#!/bin/bash

for i in ${*:2}; do
    if [[ $i == hebdate ]]; then
	    echo $(hebcal -Th); echo ""
    fi
    if [[ $i == hebcalevents ]]; then
        long_lat=$(gconftool-2 --get /apps/panel/applets/clock_screen0/prefs/cities | sed -r 's/.*(latitude.*?current=\"true\").*/\1/' | sed -r 's/latitude=\"([0-9\.\-]*)\" longitude=\"([0-9\.\-]*)\".*/\1 \2/')
	    lat=$(echo $long_lat | grep -oP "^[0-9\.\-]*")
	    long=$(echo $long_lat | grep -oP "[0-9\.\-]*$")
	    # put longitude and latitude in deg,min format. Hebcal requires that longitude sign is switched
	    lat=$(echo $lat | perl -ne '$lat = abs($_); $deg = int($lat); $min = int(60 * ($lat - $deg)); print "$deg,$min"')
	    long=$(echo $long | perl -ne '$long = abs($_); $deg = int($long); $min = int(60 * ($long - $deg)); $deg *= -1 if not /-/; print "$deg,$min"')
	    echo $(hebcal -Toc -l $lat -L $long | sed /^[0-9].*/d); echo ""
    fi
done
