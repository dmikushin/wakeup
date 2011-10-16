#!/usr/bin/python
# plugin script for EvolutionData outputting schedule and/or tasks
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import evolution, urllib, vobject, datetime, dateutil
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

# initialization
today = datetime.date.today()
todays_events = list()
all_day_events = list()
todo_list = list()

# list of calendars from evolution
calendars = evolution.ecal.list_calendars()

for cal in calendars:
    if not re.search('^webcal://', cal[1]):
        events = evolution.ecal.open_calendar_source(cal[1], evolution.ecal.CAL_SOURCE_TYPE_EVENT)
        event_list = events.get_all_objects()
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
            rrule = parsedEvent.rrule.value
            recurrences = dateutil.rrule.rrulestr(rrule, dtstart=start)
            for day in recurrences:
                if day.date() == today:
                    todays_events.append(parsedEvent)
                if day.date() > today:
                    break
        elif type(start) == datetime.date and start == today:
            d=parsedEvent.dtstart.value
            parsedEvent.dtstart.value = datetime.datetime.combine(d, datetime.time(0,0,0,0))
            todays_events.append(parsedEvent)
            all_day_events.append(parsedEvent)
        elif type(start) == datetime.datetime and start.date() == today:
            todays_events.append(parsedEvent)

    todos = evolution.ecal.open_calendar_source(cal[1],evolution.ecal.CAL_SOURCE_TYPE_TODO)
    if not todos:
        continue
    for td in todos.get_all_objects():
        parsedTd = vobject.readOne(td.get_as_string())
        if hasattr(parsedTd, "percent_complete") and parsedTd.percent_complete != "100":
            todo_list.append(parsedTd)

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
    if out == "todo":
        for td in todo_list:
            print td.summary.value + u',',
        if not todo_list:
            print "Nothing listed"
    print ""
