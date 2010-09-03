#!/usr/bin/python

# Access the Calendar events
import evolution
import re
import datetime
from string import maketrans
from dateutil.relativedelta import relativedelta
import sys
import os

# What we should output (todo or schedule)
to_output = sys.argv[2:];

# Calendars not to read (from command line arguments)
plugin = "/home/" + sys.argv[1] + "/.wakeup/" + os.environ['ALARM'] + \
         "/plugins/EvolutionData/EvolutionData.config"
plugin_file = open(plugin, "r")
lines = ''.join(plugin_file.readlines())
plugin_file.close()
skip_cals = re.search("ignore_cals\s*=\s*(.*)\s*", lines).group(1)

# translation table for converting day of week in .ics file to number
day_tr = {'MO':0,'TU':1,'WE':2,'TH':3,'FR':4,'SA':5,'SU':6}
# constants for calculating differences in time.
day = relativedelta(days=1)
week = relativedelta(weeks=1)
month = relativedelta(months=1)
year = relativedelta(years=1)

# initialization
# today must be in datetime (not date) format for comparison, make it the beginning
# of today so that events today are <= today
today = datetime.datetime.strptime(str(datetime.date.today()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
todays_events = list();


# get list of calendars from evolution
cals = evolution.ecal.list_calendars()
        
if "schedule" in to_output:
    # loop through calendars
    for i in cals:
        # get events in the calendar
        events=evolution.ecal.open_calendar_source(i[1], evolution.ecal.CAL_SOURCE_TYPE_EVENT)
        # skip specified calendars.
        if i[0] in skip_cals:
            continue;

        # loop through events
        for j in events.get_all_objects():
            props = j.get_as_string(); # string of event in .ics file
            summary = re.search("SUMMARY:(.*)\r", props).group(1)  # grab the event summary
            # check if this is an all-day event, grab date and/or time
            if re.search(".*VALUE=DATE.*", props):
                start = datetime.datetime.strptime(re.search("DTSTART.*\s*(\d{8}).*", props).group(1), "%Y%m%d")
            else:        
                start = datetime.datetime.strptime(re.search("DTSTART.*\s*(\d{8}T\d{6}).*", props).group(1), "%Y%m%dT%H%M%S")
            if start.date() > today.date():
                continue
            # figure out if the event repeats
            repeats = re.search("RRULE(.*)", props)
            # initialize. is_today = whether the correct day of week,
            # is_before_limit = whether event stops repeating after today
            is_today = False;
            is_before_limit = False;
            if repeats:
                # grab the frequency at which it repeats
                freq = re.search("FREQ=(\w*);?.*", repeats.group(1)).group(1);
                # grab whether it goes by an end date or total number of repeats
                is_until = re.search(".*UNTIL=(\d*).*;.*", repeats.group(1));
                is_counts = re.search(".*COUNT=(\w*).*", repeats.group(1));
                if freq == "WEEKLY":
                    # grab the days of the week in which it repeats
                    byday = re.search(".*BYDAY=([A-Z,]*).*", repeats.group(1));
                    if byday:
                        days = byday.group(1).split(",");
                        for day in days:
                            # convert days to numbers 0-6 and check whether that's today
                            if today.weekday() == day_tr[day]:
                                is_today = True;
                    else:
                        if today.weekday() == start.weekday():
                            is_today = True;
                    # grab the end date if appropriate and test whether before today
                    if is_until:
                        until = datetime.datetime.strptime(is_until.group(1), "%Y%m%d");
                        if today <= until:
                            is_before_limit = True;
                    # grab the number of repeats if appropriate and test whether before today
                    elif is_counts:
                        counts = is_counts.group(1);
                        if today <= start + counts * week:
                            is_before_limit = True;
                    # for a forever-repeating case
                    else:
                        is_before_limit = True;
                    if is_before_limit and is_today:
                        if re.search(".*VALUE=DATE.*", props):
                            todays_events.append((summary, ""))
                        else:
                            todays_events.append((summary, start.strftime("%-I:%M%p")))
                elif freq == "DAILY":
                    if is_until:
                        until = datetime.datetime.strptime(is_until.group(1), "%Y%m%d");
                        if today <= until:
                            is_before_limit = True;
                    elif is_counts:
                        counts = is_counts.group(1);
                        if today <= start + counts * day:
                            is_before_limit = True;
                    else:
                        is_before_limit = True;
                    if is_before_limit:
                        if re.search(".*VALUE=DATE.*", props):
                            todays_events.append((summary, ""))
                        else:
                            todays_events.append((summary, start.strftime("%-I:%M%p")))
                elif freq == "MONTHLY":
                    day_of_month = re.search("BYMONTHDAY=(\w*).*", tmp).group(1);
                    if is_until:
                        until = datetime.datetime.strptime(is_until.group(1), "%Y%m%d");
                        if today <= until:
                            is_before_limit = True;
                    elif is_counts:
                        counts = is_counts.group(1);
                        if today <= start + counts * month:
                            is_before_limit = True;
                    else:
                        is_before_limit = True;
                    if is_before_limit and today.day == day_of_month:
                        if re.search(".*VALUE=DATE.*", props):
                            todays_events.append((summary, ""))
                        else:
                            todays_events.append((summary, start.strftime("%-I:%M%p")))
                elif freq == "YEARLY":
                    if is_until:
                        until = datetime.datetime.strptime(is_until.group(1), "%Y%m%d");
                        if today <= until:
                            is_before_limit = True;
                    elif is_counts:
                        counts = is_counts.group(1);
                        if today <= start + counts * year:
                            is_before_limit = True;
                    else:
                        is_before_limit = True;
                    if is_before_limit and today.day == start.day and today.month == start.month:
                        if re.search(".*VALUE=DATE.*", props):
                            todays_events.append((summary, ""))
                        else:
                            todays_events.append((summary, start.strftime("%-I:%M%p")))
            # if non-repeating, start date is only date.
            else:
                if start.date() == today.date():
                    if re.search(".*VALUE=DATE.*", props):
                        todays_events.append((summary, ""))
                    else:
                        todays_events.append((summary, start.strftime("%-I:%M%p")))


    # print out a list of tuples ("summary", "HH:MM")
    #print todays_events
    event_list = ""
    for i in todays_events:
        event_list += i[0]
        if i[1] != "":
            event_list += " at " + i[1] + ".........\\n....\\n"
        event_list += ".........\\n....\\n"
    if event_list == "":
        event_list = "Nothing listed."

if "todo" in to_output:
    todos = evolution.ecal.open_calendar_source('default',evolution.ecal.CAL_SOURCE_TYPE_TODO)
    todo_list = ""
    if todos:
        for k in todos.get_all_objects():
            percent_complete = re.search("PERCENT-COMPLETE:(.*)\r", k.get_as_string());
            if not percent_complete or percent_complete.group(1) != "100":
                todo_list += re.search("SUMMARY:(.*)\r", k.get_as_string()).group(1) + ".........\\n....\\n";
    if todo_list == "":
        todo_list = "Nothing listed."


for output in to_output:
    if output == "schedule":
        print event_list + "\n"
    if output == "todo":
        print todo_list + "\n"
