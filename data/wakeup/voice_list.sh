#!/bin/bash
# Output a list of "voicename\ndescription" for each voice available to
# festival. Uses voice name as description if no description found.
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

out1=/tmp/voice_out1
out2=/tmp/voice_out2
out3=/tmp/voice_out3
echo "" > $out1; echo "" > $out2; echo "" > $out3
festival --server >/dev/null 2>&1 &

festival_id=$!

while [[ $(echo '()' | festival_client && echo $?) != 0 ]]; do
echo -n ''
done >/dev/null 2>&1

echo "(pprintf (voice.list) (fopen \"$out1\" \"w\"))" | festival_client
voices=($(cat $out1 | sed 's/[()]//g'))

for voice in ${voices[@]}; do
    echo "(pprintf (voice.description '$voice) (fopen \"$out2\" \"w\"))" | festival_client
    echo $voice >> $out3
    description=$(echo $(cat $out2) | grep -oP '(description "[^)(]*")')
    if [[ $description == "" ]]; then
        echo $voice >> $out3
    else
        echo $description | sed -e 's/description //' -e 's/"//g' >> $out3
    fi
done

cat $out3 | sed '/^$/d'
rm $out1 $out2 $out3
kill $festival_id >/dev/null 2>&1
