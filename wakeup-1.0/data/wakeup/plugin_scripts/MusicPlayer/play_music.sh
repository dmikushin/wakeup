#!/bin/bash
# plugin script for MusicPlayer, which plays a given file with mpg123
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

plugin_file=/home/$1/.wakeup/$ALARM/plugins/MusicPlayer/MusicPlayer.config
MUSIC=$(sed -rn 's/music_file\s*=\s*(.*)\s*$/\1/p' $plugin_file)
ENDPOS=$(sed -rn 's/time\s*=\s*(.*)\s*$/\1/p' $plugin_file)
echo "hello: $ENDPOS"
# note making volume 3/4 is a hack to make the music volume equal the
# low festival volume. It only needs to be done when not logged in.
if [[ `who` == "" ]]; then
    volume=$(sudo /usr/bin/amixer get Master | grep -oP "\d+%" | grep -oP "\d+")
    sudo /usr/bin/amixer set Master $(($volume * 3 / 4))\%
fi

if [[ $ENDPOS == 0 ]]; then
    mpg123 "$MUSIC"
else
    mpg123 "$MUSIC" &
    x=$!
    if [[ $ENDPOS =~ [0-9]+:[0-9]{2} ]]; then
        mins=$(echo $ENDPOS | grep -oP "^[0-9]+")
        secs=$(echo $ENDPOS | grep -oP "[0-9]+$")
        ENDPOS=$(( 60 * mins + secs ))
    fi
    sleep $ENDPOS
    kill $x
fi
#reset volume
if [[ `who` == "" ]]; then
    sudo /usr/bin/amixer set Master $volume\%
fi
