#!/bin/bash

eval $(cat /home/$1/.wakeup/$ALARM/plugins/GmailCounter/GmailCounter.config);
password=$(echo $password | base64 -d)

tmpfile=/tmp/gmailcheck_tmp
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
