#!/usr/bin/env python
# Using setalarm, finds the earliest alarm in the future which requires
# a computer wakeup and sets the computer to wake up and run that alarm. 
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import sys
import os
import re
wakeup_script = "/usr/bin/wakeup"
wakeup_folder = "/usr/share/wakeup/"
sys.path.append(wakeup_folder)
from alarm import alarm
import subprocess

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
    crontimes.append(re.sub('"', '', cronstring))
    try:
        output = subprocess.check_output([setalarm_script, '-p', '-c'] + re.split(' ', cronstring) +  ['-o', '0'])
        alarmtimes.append(output)
    except subprocess.CalledProcessError:
        if output == "The specified cron time does not occur within a year":
            del alarms[alarms.index(alarm)]
        else:
            print "Unable to set alarms. Some crontimes are invalid."
            exit(1)

# If no alarms in list, clear root's cron file and unset computer wakeup
if len(alarms) == 0:
    tmpfile = '/tmp/setnextalarm_tmp.txt'
    f = open(tmpfile, 'w')
    subprocess.call(['sudo', 'crontab', '-l'], stdout=f)
    f.close()
    subprocess.call(['sed', '-i', '/^.*setnextalarm.*$/d', tmpfile])
    subprocess.call(['sudo', 'crontab', tmpfile])
    subprocess.call(['rm', tmpfile])
    subprocess.call(['sudo', setalarm_script, '-d'])
    exit()

minalarm = min(alarmtimes)
minindex = alarmtimes.index(minalarm)
mincron = crontimes[minindex]
# make sure the wakeup is preserved through shutdowns and at alarm times. Set alarms.
tmpfile = '/tmp/setnextalarm_tmp.txt'
f = open(tmpfile, 'w')
subprocess.call(['sudo', 'crontab', '-l'], stdout=f)
subprocess.call(['sed', '-i', '/^.*setnextalarm.*$/d', tmpfile])
f.close()
f = open(tmpfile, 'a')
f.write(mincron + ' ' + thisscript +  ' >/dev/null 2>&1\n')
f.write('@reboot ' + thisscript + ' >/dev/null 2>&1\n')
for i in range(0, len(alarmtimes)):
    if alarmtimes[i] == minalarm:
        alarmnum = re.search("\d+$", alarmfolders[i]).group(0)
        f.write(mincron + ' ' + wakeup_script + ' ' + sys.argv[1] + ' ' + alarmnum + \
                ' >/dev/null 2>&1 #entered by setnextalarm\n')
f.close()
subprocess.call(['sudo', 'crontab', tmpfile])
subprocess.call(['rm', tmpfile])
success = True
try:
    subprocess.check_output(['sudo', setalarm_script, '-u', minalarm])
except subprocess.CalledProcessError:
    success = False
try:
    output = subprocess.check_output(['date', '-d', '@' + minalarm])
    print output
except subprocess.CalledProcessError:
    success = False
if not success:
    print "Unable to set alarms. Check alarm time preferences."
    exit(1)
