#!/bin/bash
# Run user-defined commands
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

IFS=,
plugin_file=/home/$1/.wakeup/$ALARM/plugins/Commands/Commands.config
dataitems=($(sed -rn 's/dataitems\s*=\s*(.*)\s*$/\1/p' $plugin_file))
scripts=($(sed -rn 's/scripts\s*=\s*(.*)\s*$/\1/p' $plugin_file))

# Make hash of dataitems->scripts
declare -A itemscripts
for (( i = 0; i < ${#dataitems[@]}; i++ )); do
    itemscripts[${dataitems[$i]}]=${scripts[$i]}
done

# Execute scripts and output any text output properly
for item in ${*:2}; do
    eval ${itemscripts[$item]} 2>/dev/null; echo ""
done
