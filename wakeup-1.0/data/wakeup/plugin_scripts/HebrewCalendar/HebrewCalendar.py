#!/usr/bin/env python
# plugin GUI preferences class for Hebrew Calendar
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re
import commands
import threading

class HebrewCalendar:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("HebrewCalendar.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.set_manual_location = self.wTree.get_object("checkbutton1")
        self.longitude = self.wTree.get_object("entry1")
        self.latitude = self.wTree.get_object("entry2")
        self.plugin_file = os.path.join(pluginfolder, 'HebrewCalendar.config')
        hc_file = open(self.plugin_file, "r")
        self.lines = ''.join(hc_file.readlines())
        hc_file.close()
        old_manual_location = re.search("manual_location\s*=\s*(.*)\s*", self.lines).group(1)
        if old_manual_location == "true":
            old_longitude = re.search("longitude\s*=\s*(.*)\s*\n", self.lines).group(1)
            old_latitude = re.search("latitude\s*=\s*(.*)\s*", self.lines).group(1)
        else:
            old_longitude = ""
            old_latitude = ""
        self.set_manual_location.set_active(old_manual_location == "true")
        self.longitude.set_sensitive(old_manual_location == "true")
        self.latitude.set_sensitive(old_manual_location == "true")
        if old_manual_location == "false":
            thread = self.LonLatThread(self)
            thread.start()
        else:
            self.longitude.set_text(old_longitude)
            self.latitude.set_text(old_latitude)

    # Thread so we don't have to wait for autolocation to be found
    class LonLatThread (threading.Thread):
        def __init__(self, parent):
            self.window = parent
            threading.Thread.__init__(self)
        def run(self):
            self.window.LonLat = commands.getoutput('wget -q -U DummyBrowser/1.0 -O - www.ip-adress.com/ip_tracer | grep GLatLng | grep -oP "[0-9\.\-, ]{2,}"')
            lon = re.search("^[0-9\.\-]+", self.window.LonLat).group(0)
            lat = re.search("[0-9\.\-]+$", self.window.LonLat).group(0)
            self.window.longitude.set_text(lon)
            self.window.latitude.set_text(lat)


    '''On Checking to set weather ID manually'''
    def on_manualLonLat_toggled(self, widget, data=None):
        self.longitude.set_sensitive(widget.get_active())
        self.latitude.set_sensitive(widget.get_active())

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        if self.set_manual_location.get_active():
            lon = self.longitude.get_text()
            lat = self.latitude.get_text()
            manual_location = "true"
        else:
            lon=""
            lat=""
            manual_location = "false"
        #self.lines = re.sub("longitude\s*=\s*.*\s*", "longitude=" \
        #    + lon + "\n", self.lines)
        #self.lines = re.sub("latitude\s*=\s*.*\s*", "latitude=" \
        #    + lat + "\n", self.lines)
        #self.lines = re.sub("manual_location\s*=\s*.*\s*", "manual_location=" \
        #    + manual_location + "\n", self.lines)
        hc_file = open(self.plugin_file, "w")
        hc_file.write("longitude=" + lon + "\n")
        hc_file.write("latitude=" + lat + "\n")
        hc_file.write("manual_location=" + manual_location)
        hc_file.close()
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
