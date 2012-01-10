#!/bin/bash
# plugin script for GmailCounter outputting number of new emails on a gmail account.
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

eval $(cat /home/$1/.wakeup/$ALARM/plugins/GmailCounter/GmailCounter.config);
password=$(echo $password | base64 -d)

tmpfile=$(mktemp)
curl -u $username:$password --silent "https://mail.google.com/mail/feed/atom" \
		| grep -P "<issued>.*" | sed -r 's/(.*)T24:(.*)/\1T0:\2/' \
		| sed -r 's/<issued>(.*)T(.*)Z<\/issued>/date +%s --date "\1 \2"/' > $tmpfile
chmod +x $tmpfile
times=($($tmpfile))
last_checked=$(curl -u $username:$password --silent \
		"https://mail.google.com/mail/feed/atom" | grep -m 1 "<modified>" \
		| sed -r 's/(.*)T24:(.*)/\1T0:\2/' \
		| sed -r 's/<modified>(.*)T(.*)Z<\/modified>/\1 \2/')
last_checked=$(date +%s --date "$last_checked -1 hour")

num_new_emails=0;
for i in ${times[@]}; do 
	if [[ $i > $last_checked ]]; then 
		num_new_emails=$(( $num_new_emails + 1 ));
	fi
done

rm $tmpfile

plural="s"; if [[ $num_new_emails == 1 ]]; then plural=""; fi
echo "$num_new_emails new e-mail$plural"
