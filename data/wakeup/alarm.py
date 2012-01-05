#!/usr/bin/env python
# alarm data type class used by wakeup-settings and setnextalarm.
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import datetime, re, os, pickle, subprocess
days_dict = dict(Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6)

class alarm:

    def __init__(self):
        # Default values
        self.text = ""
        self.time = [8, 30]
        self.recurrs = False
        self.recurrence = "None"
        self.day_recurrences = dict(Sun=False, Mon=False, Tue=False,
                                    Wed=False, Thu=False, Fri=False,
                                    Sat=False)
        self.dom = 1
        self.mon = "*"
        self.cronvalue = "0 0 0 0 0"
        self.volume = 70
        self.voice = "none"
        self.otherspeechtool = "none"
        self.wakecomputer = True
        self.activeplugins = list()
        self.Commands_dataitems = list() # for dynamic dataitems from Commands plugin
            
    def set_property(self, property_name, value):
        exec("self." + property_name + " = value")
    
    def get_property(self, property_name):
        exec("prop = self." + property_name)
        return prop
        
    def save_playfile(self, filename, folder, isTmpFile, plugins):
        data_items = list()
        itemsToPlugin = dict()
        for key in plugins.keys():
            data_items.extend(plugins[key]['data_items'])
            for item in plugins[key]['data_items']:
                itemsToPlugin[item] = key
        # Add in dynamic dataitems from Commands plugin
        if "Commands" in self.activeplugins:
            data_items.extend(self.Commands_dataitems)
            for item in self.Commands_dataitems:
                itemsToPlugin[item] = "Commands"

        usedDataByPlugin = dict()
        for name in self.activeplugins:
            usedDataByPlugin[name] = list()            
        strings = re.split("\n{2,}", self.text)
        final_text = ""
        sudo = ""
        if self.wakecomputer and not isTmpFile:
            sudo = "sudo -E -u $usr "
        for i in strings:
            has_text_output = False
            items = re.findall("\$\w+", i)
            for j in range(len(items)):
                items[j] = items[j][1:]
            keys = {}
            for j in items:
                keys[j] = 1
            data_used = keys.keys()
            init_string = ""
            for name in usedDataByPlugin.keys():
                del usedDataByPlugin[name][:]
            for j in data_used:
                if j in data_items and itemsToPlugin[j] in self.activeplugins:
                    usedDataByPlugin[itemsToPlugin[j]].append(j)
                else:
                    i = re.sub('\$'+j,'\\\$'+j,i)
                    del data_used[data_used.index(j)]
            for name in usedDataByPlugin.keys():
                if plugins[name]['text_output'] and not len(usedDataByPlugin[name]) == 0:
                    itemsstring = "".join([k + " " for k in usedDataByPlugin[name]])
                    init_string += "data=($(echo \"$(" + sudo + plugins[name]['script'] + \
                                   " $usr " + itemsstring + \
                                   ")\" | sed -r ':a;N;$!ba;s/\\n{2}/ \\n\\n/g'));\n"
                    for k in range(len(usedDataByPlugin[name])):
                        init_string += usedDataByPlugin[name][k] + "=${data[" + str(k) + "]}; "
                    init_string += "\n"
                    has_text_output = True
                else:
                    for item in usedDataByPlugin[name]:
                        #note there is no sudo for non-text items
                        init_string += plugins[name]['script'] + " $usr\n"
            final_text += "\n" + init_string
            if has_text_output or len(data_used) == 0:\
                final_text += "echo -e \"" + i + "\" | talk\n"
        file = open(filename, "w")
        file.write("#!/bin/bash\nusr=$1\n")
        file.write("export ALARM=" + folder + "\nIFS=$'\\n\\n'\nshopt -s expand_aliases\n")
        if not self.otherspeechtool == "none":
            file.write("alias talk='" + self.otherspeechtool + "'\n\n")
        else:
            file.write("alias talk='festival_client --ttw | aplay'\n")
            file.write("festival --server ")
            if self.voice != "none":
                file.write("'(voice_" + self.voice + ")'")
            file.write("&\nwhile [[ $(echo '()' | festival_client && echo $?) != 0 ]];" \
                     + " do echo -n ''; done\n\n")
        file.write(final_text)
        file.close()
        subprocess.call(["chmod", "+x", filename])
        
    def save_settings(self, filename):
        cronval = ""
        for i in self.get_cronvalues():
            cronval += str(i) + " "
        self.cronvalue = cronval.strip()
        alarm_file = open(filename, "w")
        pickle.dump(self, alarm_file)
        alarm_file.close()
        
    def read_settings(self, filename):
        try:
            alarm_file = open(filename, "r")
            tmpalarm = pickle.load(alarm_file)
            alarm_file.close()
            self.text = tmpalarm.get_property("text")
            self.time = tmpalarm.get_property("time")
            self.recurrs = tmpalarm.get_property("recurrs")
            self.recurrence = tmpalarm.get_property("recurrence")
            self.day_recurrences = tmpalarm.get_property("day_recurrences")
            self.dom = tmpalarm.get_property("dom")
            self.mon = tmpalarm.get_property("mon")
            self.cronvalue = tmpalarm.get_property("cronvalue")
            self.volume = tmpalarm.get_property("volume")
            self.voice = tmpalarm.get_property("voice")
            self.otherspeechtool = tmpalarm.get_property("otherspeechtool")
            self.wakecomputer = tmpalarm.get_property("wakecomputer")
            self.activeplugins = tmpalarm.get_property("activeplugins")
        except: return "wakeup_settings file not found or improperly formatted"
        return "Loaded wakeup settings"
        
    def setalarm_command(self, folder, setalarm_script, wakeup_script):
        [minute, hour, dom, mon, dow] = self.get_cronvalues()
        alarmnum = re.search("alarm(\d+)$", folder).group(1)
        wakeup_script_meta = re.sub("/", "\\/", wakeup_script)
        if self.wakecomputer:
            if self.recurrs == False:
                # workaround for minute spinbutton having only 1 digit for minutes < 10
                if minute < 10:
                    minute = "0" + str(minute)
                command = setalarm_script + " " + str(hour) +  ":" \
                        + str(minute) + " " + wakeup_script + " " + os.environ['USER'] + " " + alarmnum
            else:
                # Note, because shell=False in check_output, do not need to quote asterisks
                command = setalarm_script + ' -c ' + str(minute) + ' ' \
                        + str(hour) + ' ' + str(dom) + ' ' + str(mon) \
                        + ' ' + str(dow) + ' ' + wakeup_script + " " + os.environ['USER'] + " " + alarmnum
            pre = ['gksudo', '--message', 'Root privileges are necessary to set and remove alarms that wake your computer']
            command = pre + [command]
            try:
                out = subprocess.check_output(command)
                return [0, out]
            except subprocess.CalledProcessError:
                return [1, ""]
        else:
            tmpfile = "/tmp/wakeup_tmp.txt"
            f = open(tmpfile,'w')
            subprocess.call(['crontab', '-l'], stdout=f)
            subprocess.call(['sed', '-i', "/^.*" + wakeup_script_meta + " " + os.environ['USER'] + " " \
                    + alarmnum + ".*$/d", tmpfile])
            f.close()
            f = open(tmpfile,'a')
            f.write(str(minute) + " " + str(hour) + " " + str(dom) + " " + str(mon) + " " + str(dow))
            f.write(" " + wakeup_script + " " + os.environ['USER'] + " " + alarmnum + " >/dev/null 2>&1\n")
            f.close()
            subprocess.call(['crontab', tmpfile])
            subprocess.call(['rm', tmpfile])
            return [0,""]

    def remove_command(self, folder, wakeup_script):
        alarmnum = re.search("alarm(\d+)$", folder).group(1)
        wakeup_script_meta = re.sub("/", "\\/", wakeup_script)
        sudo = []
        if self.wakecomputer:
            sudo = ['gksudo', '--message', 'Root privileges are necessary to set and remove alarms that wake your computer']
        tmpfile = "/tmp/wakeup_tmp.txt"
        f = open(tmpfile, 'w')
        if sudo != []:
            subprocess.call(sudo + ['crontab -l'], stdout=f)
        else:
            subprocess.call(['crontab', '-l'], stdout=f)
        f.close()
        subprocess.call(['sed', '-i', "/^.*" + wakeup_script_meta + " " + os.environ['USER'] + " " \
                        + alarmnum + ".*$/d", tmpfile])
        if sudo != []:
            subprocess.call(sudo + ['crontab ' + tmpfile])
        else:
            subprocess.call(['crontab', tmpfile])
        subprocess.call(['rm', tmpfile])

    def get_cronvalues(self):
        if self.recurrence == "Cron":
            try:
                [minute, hour, dom, mon, dow] = re.split("\s+", self.cronvalue)
            except:
                print self.cronvalue + "\n      Failed to set alarm.      \nBad Cron setting"
                return [0, 0, 0, 0, 0]
        elif self.recurrence == "None":
            [minute, hour, dom, mon, dow] = [int(self.time[1]), int(self.time[0]),
                                             "-1", "-1", "-1"]
            now = datetime.datetime.now()
            if now.hour > hour or (now.hour == hour and now.minute >= minute):
                now = now + datetime.timedelta(days=1)
            (dom, mon, dow) = (now.day, now.month, now.isoweekday())
            if dow == 7:
                dow = 0
        elif self.recurrence == "Month":
            [minute, hour, dom, mon, dow] = [int(self.time[1]), int(self.time[0]),
                                             int(self.dom), "*", "*"]
        elif self.recurrence == "Week":
            days = ""
            for i in self.day_recurrences.iterkeys():
                if self.day_recurrences[i]:
                    days += str(days_dict[i]) + ","
            days = days.rstrip(",")
            [minute, hour, dom, mon, dow] = [int(self.time[1]), int(self.time[0]),
                                             "*", "*", days]
        elif self.recurrence == "Day":
            [minute, hour, dom, mon, dow] = [int(self.time[1]), int(self.time[0]),
                                             "*", "*", "*"]
        elif self.recurrence == "Hour":
            [minute, hour, dom, mon, dow] = [int(self.time[1]), "*", "*", "*", "*"]
        elif self.recurrence == "Minute":
            [minute, hour, dom, mon, dow] = ["*", "*", "*", "*", "*"]
        return [minute, hour, dom, mon, dow]
