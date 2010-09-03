#!/bin/bash

plugin_file=/home/$1/.wakeup/$ALARM/plugins/MusicPlayer/MusicPlayer.config
MUSIC=$(sed -rn 's/music_file\s*=\s*(.*)\s*$/\1/p' $plugin_file)
ENDPOS=$(sed -rn 's/time\s*=\s*(.*)\s*$/\1/p' $plugin_file)

# note making volume 3/4 is a hack to make the music volume equal the
# low festival volume. It only needs to be done when not logged in.
if [[ `who` == "" ]]; then
    volume=$(sudo /usr/bin/amixer get Master | grep -oP "\d+%" | grep -oP "\d+")
    sudo /usr/bin/amixer set Master $(($volume * 3 / 4))\%
fi

if [[ $ENDPOS == 0 ]]; then
    mplayer "$MUSIC"
else
    mplayer "$MUSIC" -endpos $ENDPOS
fi
#reset volume
if [[ `who` == "" ]]; then
    sudo /usr/bin/amixer set Master $volume\%
fi
