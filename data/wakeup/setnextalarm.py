#!/usr/bin/env python
# Using setalarm, finds the earliest alarm in the future which requires
# a computer wakeup and sets the computer to wake up and run that alarm. 
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import sys
import os
import re
wakeup_script = "/usr/bin/wakeup"
wakeup_folder = "/usr/share/wakeup/"
sys.path.append(wakeup_folder)
from alarm import alarm
from commands import getstatusoutput

thisscript = os.path.join(wakeup_folder, "setnextalarm.py") + " " + sys.argv[1]
setalarm_script = "/usr/bin/setalarm"
home = os.path.join('/home', sys.argv[1])
homewakeupfolder = os.path.join(home, ".wakeup")
alarms = list()
alarmfolders = list()
# Load alarms, and specifically their times (don't need text, plugins, etc.)
for foldername in os.listdir(homewakeupfolder):
    folder = os.path.join(homewakeupfolder, foldername)
    if not re.search("alarm\d+$", folder) or not os.path.isdir(folder):
        continue
    alarms.append(alarm())
    alarmfolders.append(folder)
    alarms[-1].read_settings(os.path.join(folder, "wakeup_settings"))
    if not alarms[-1].get_property("wakecomputer"):
        del alarms[-1]
        del alarmfolders[-1]
    
# Get alarm cron times and find the time to wake the computer for each
alarmtimes = list()
crontimes = list()
for alarm in alarms:
    cronstring = alarm.get_property("cronvalue")
    cronstring = re.sub("\*", '"*"', cronstring)
    [status, output] = getstatusoutput(setalarm_script + " -p -c " + \
                                       cronstring + " -o 0")
    if status == 0:
        alarmtimes.append(output)
        crontimes.append(re.sub('"', '', cronstring))
    elif output == "The specified cron time does not occur within a year":
        del alarms[alarms.index(alarm)]
    else:
        print "Unable to set alarms. Some crontimes are invalid."
        exit(1)

# If no alarms in list, clear root's cron file and unset computer wakeup
if len(alarms) == 0:
    [status1, output] = getstatusoutput('tmpfile=/tmp/setnextalarm_tmp.txt\n' + \
                    'sudo crontab -l > $tmpfile\n' + \
                    'sed -i /^.*setnextalarm.*$/d $tmpfile\n' + \
                    'sudo crontab $tmpfile\n' + \
                    'rm $tmpfile')
    [status2, output] = getstatusoutput('sudo ' + setalarm_script + ' -u 0')
    exit()

minalarm = min(alarmtimes)
minindex = alarmtimes.index(minalarm)
mincron = crontimes[minindex]
# make sure the wakeup is preserved through shutdowns and at alarm times. Set alarms.
command = 'tmpfile=/tmp/setnextalarm_tmp.txt\n' + \
          'sudo crontab -l > $tmpfile\n' + \
          'sed -i /^.*setnextalarm.*$/d $tmpfile\n' + \
          'echo \'' + mincron + ' ' + thisscript + \
          ' >/dev/null 2>&1\' >> $tmpfile\n' + \
          'echo \'@reboot ' + thisscript + \
          ' >/dev/null 2>&1\' >> $tmpfile\n'
for i in range(0, len(alarmtimes)):
    if alarmtimes[i] == minalarm:
        alarmnum = re.search("\d+$", alarmfolders[i]).group(0)
        command += 'echo \'' + mincron + ' ' + \
                   wakeup_script + " " + sys.argv[1] + " " + alarmnum + \
                   ' >/dev/null 2>&1 #entered by setnextalarm\' >> $tmpfile\n'
command += 'sudo crontab $tmpfile\n' + \
           'rm $tmpfile'
[status1, output] = getstatusoutput(command)
# set the computer to wake at the earliest of the wakeup times
[status2, output] = getstatusoutput('sudo ' + setalarm_script + ' -u ' + minalarm)
if status1 == 0 and status2 == 0:
    [status, output] = getstatusoutput('date -d @' + minalarm)
    print output
else:
    print "Unable to set alarms. Check alarm time preferences."
    exit(1)
