#!/bin/bash
# plugin script for Weather outputting various weather conditions
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

plugin_file="/home/$1/.wakeup/$ALARM/plugins/Weather/Weather.config"
manual_location=$(sed -rn 's/location\s*=\s*(.*)\s*/\1/p' $plugin_file)
if [[ $manual_location == "none" ]]; then
    $(dirname $0)/format_weather.pl $($(dirname $0)/id_by_ip.sh) $1 $ALARM ${*:2}
else
    $(dirname $0)/format_weather.pl $manual_location $1 $ALARM ${*:2}
fi
