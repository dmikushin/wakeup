#!/bin/bash

settings=$(gconftool-2 --get /apps/panel/applets/clock_screen0/prefs/cities)
home=$(echo $settings | grep -oP "code=\"\w*\" current=\"true\"" | grep -oP "[A-Z]{4}")
plugin_file="/home/$1/.wakeup/$ALARM/plugins/Weather/Weather.config"
manual_location=$(sed -rn 's/location\s*=\s*(.*)\s*/\1/p' $plugin_file)
if [[ $manual_location == "none" ]]; then
    $(dirname $0)/format_weather.pl $home $1 $ALARM ${*:2}
else
    $(dirname $0)/format_weather.pl $manual_location $1 $ALARM ${*:2}
fi
