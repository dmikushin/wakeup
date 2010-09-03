#!/bin/bash

plugin_file=/home/$1/.wakeup/$ALARM/plugins/DateTime/DateTime.config
date_format=$(sed -rn 's/date_format\s*=\s*(.*)\s*$/\1/p' $plugin_file)
time_format=$(sed -rn 's/time_format\s*=\s*(.*)\s*$/\1/p' $plugin_file)

for i in ${*:2}; do
    if [[ $i == date ]]; then
	    echo $(date +"$date_format"); echo ""
    elif [[ $i == time ]]; then
	    echo $(date +"$time_format"); echo ""
    fi
done
