#!/bin/bash
# plugin script for LastfmPlayer, a wrapper for shell-fm
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

trap "killall shell-fm; exit" SIGHUP SIGINT SIGTERM

export HOME=/home/$1
plugin_file=~/.shell-fm/shell-fm.rc
duration=$(sed -rn 's/#duration\s*=\s*(.*)\s*/\1/p' $plugin_file)

if [[ $duration == 0 ]]; then
    shell-fm
else
    ip=$(ifconfig -a | grep -oP "inet addr:[0-9\.]+" -m 1 | sed -r 's/inet addr://')
    shell-fm -i $ip -d
    if [[ $duration =~ [0-9]+:[0-9]{2} ]]; then
        mins=$(echo $duration | grep -oP "^[0-9]+")
        secs=$(echo $duration | grep -oP "[0-9]+$")
        duration=$(( 60 * mins + secs ))
    fi
    sleep $duration
    killall shell-fm
fi
