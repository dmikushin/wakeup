#!/usr/bin/python
# plugin script for EvolutionData outputting schedule and/or tasks
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import urllib, vobject, datetime, dateutil
import sys, os
import re

# What we should output (todo and/or schedule)
to_output = sys.argv[2:]

# Calendars not to read (from command line arguments)
plugin = "/home/" + sys.argv[1] + "/.wakeup/" + os.environ['ALARM'] + \
         "/plugins/EvolutionData/EvolutionData.config"
plugin_file = open(plugin, "r")
lines = ''.join(plugin_file.readlines())
plugin_file.close()
skip_cals = re.search("ignore_cals\s*=\s*(.*)\s*", lines).group(1)
calendarsfolder = '/home/' + sys.argv[1] + '/.local/share/evolution/calendar'
tasksfolder = '/home/' + sys.argv[1] + '/.local/share/evolution/tasks'

# initialization
today = datetime.date.today()
todays_events = list()
all_day_events = list()
todo_list = list()

# list of calendars from evolution
calendars = []
for root, dirs, files in os.walk(calendarsfolder):
    for _file in files:
        if _file.endswith('.ics'):
            calendars.append(os.path.join(root,_file))
# list of tasks
tasklists = []
for root, dirs, files in os.walk(tasksfolder):
    for _file in files:
        if _file.endswith('.ics'):
            tasklists.append(os.path.join(root,_file))



for cal in calendars:
    if not re.search('^webcal://', cal[1]):
        f = open(cal)
        calstring = ''.join(f.readlines())
        f.close()
        try:
            event_list = vobject.readOne(calstring).vevent_list
        except AttributeError:
            continue
    else: # evolution library does not support webcal ics
        webcal = urllib.urlopen('http://' + cal[1][9:])
        webcalstring = ''.join(webcal.readlines())
        webcal.close()
        event_list = vobject.readOne(webcalstring).vevent_list
    if cal[0] in skip_cals:
        continue

    # loop through events
    for ev in event_list:
        if type(ev) != vobject.icalendar.RecurringComponent:
            parsedEvent = vobject.readOne(ev.get_as_string())
        else:
            parsedEvent = ev
        start = parsedEvent.dtstart.value
        if hasattr(parsedEvent, "rrule"):
            try:
                rrule = parsedEvent.rrule.value
                rrule_until = re.search("UNTIL=[A-Za-z0-9]+",rrule)
                if rrule_until and rrule_until.group(0)[-1] == "Z": # some weird dateutil error in time zones
                    rrule = re.sub(rrule_until.group(0), rrule_until.group(0)[:-1], rrule)
                recurrences = dateutil.rrule.rrulestr(rrule, dtstart=start)
                for day in recurrences:
                    if day.date() == today:
                        todays_events.append(parsedEvent)
                    if day.date() > today:
                        break
            except TypeError:
                pass # some weird dateutil error in time zones, just in case it's still missed
        elif type(start) == datetime.date and start == today:
            d=parsedEvent.dtstart.value
            parsedEvent.dtstart.value = datetime.datetime.combine(d, datetime.time(0,0,0,0))
            todays_events.append(parsedEvent)
            all_day_events.append(parsedEvent)
        elif type(start) == datetime.datetime and start.date() == today:
            todays_events.append(parsedEvent)

for tasklist in tasklists:
    f = open(tasklist)
    taskliststring = ''.join(f.readlines())
    f.close()
    try:
        todos = vobject.readOne(taskliststring).vtodo_list
        for td in todos:
            if not (hasattr(td, "percent_complete") and td.percent_complete == "100"):
                todo_list.append(td)
    except AttributeError:
        pass

for out in to_output:
    if out == "schedule":
        for ev in sorted(todays_events,key=lambda e: e.dtstart.value):
            print ev.summary.value,
            if not ev in all_day_events:
                print u'at ' + ev.dtstart.value.strftime("%l:%M %p"),
            if hasattr(ev, "location"):
                print u'in ' + ev.location.value,
            print ", ",
        if not todays_events:
            print "Nothing listed"
        print ""
    if out == "todo":
        for td in todo_list:
            print td.summary.value + u',',
        if not todo_list:
            print "Nothing listed"
    print ""
