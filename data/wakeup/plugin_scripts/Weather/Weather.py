#!/usr/bin/env python
# plugin GUI preferences class for Weather
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re
import subprocess, threading

class Weather:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("Weather.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.manual_id = self.wTree.get_object("entry1")
        self.set_manual = self.wTree.get_object("checkbutton1")
        self.temp_units = self.wTree.get_object("combobox1")
        self.wind_units = self.wTree.get_object("combobox2")
        self.plugin_file = os.path.join(pluginfolder, 'Weather.config')
        ws_file = open(self.plugin_file, "r")
        self.lines = ''.join(ws_file.readlines())
        ws_file.close()
        old_temp_units = re.search("temperature_units\s*=\s*(.*)\s*", self.lines).group(1) != "F"
        old_wind_units = re.search("wind_units\s*=\s*(.*)\s*", self.lines).group(1) != "mph"
        old_location = re.search("location\s*=\s*(.*)\s*", self.lines).group(1)
        self.temp_units.set_active(old_temp_units)
        self.wind_units.set_active(old_wind_units)
        
        if old_location == "none":
            thread = self.ipThread(self.manual_id)
            thread.start()
        else:
            self.manual_id.set_text(old_location)
        if not old_location == "none":
            self.manual_id.set_sensitive(False)
            self.set_manual.set_active(True)

    # Thread so we don't have to wait for autolocation to be found
    class ipThread (threading.Thread):
        def __init__(self, manual_id):
            self.location = manual_id
            threading.Thread.__init__(self)
        def run(self):
            import location
            loc = location.get_location()
            self.location.set_text(loc['City']+','+loc['State']+','+loc['Country'])


    '''On Checking to set weather ID manually'''
    def on_manualID_toggled(self, widget, data=None):
        self.manual_id.set_sensitive(widget.get_active())

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        if self.temp_units.get_active() == 0:
            temp_units = "F"
        else:
            temp_units = "C"
        if self.wind_units.get_active() == 0:
            wind_units = "mph"
        else:
            wind_units = "knots"
        if self.set_manual.get_active():
            location = self.manual_id.get_text()
        else:
            location = "none" #self.auto_location
        self.lines = re.sub("temperature_units\s*=\s*.*\s*", "temperature_units=" \
            + temp_units + "\n", self.lines)
        self.lines = re.sub("wind_units\s*=\s*.*\s*", "wind_units=" \
            + wind_units + "\n", self.lines)
        self.lines = re.sub("location\s*=\s*.*\s*", "location=" \
            + location + "\n", self.lines)
        ws_file = open(self.plugin_file, "w")
        ws_file.write(self.lines)
        ws_file.close()
        self.on_window_destroy(self)

    '''On Clicking Cancel'''
    def on_cancel_clicked(self, widget, data=None):
        self.on_window_destroy(self)

    '''Exit'''
    def on_window_destroy(self, widget, data=None):
        self.window.destroy()
        gtk.main_quit()

    '''Run the GUI'''
    def main(self):
        gtk.gdk.threads_init()
        gtk.main()
