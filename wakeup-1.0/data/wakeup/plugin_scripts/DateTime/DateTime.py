#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re

class DateTime:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("DateTime.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.date = self.wTree.get_object("entry1")
        self.time = self.wTree.get_object("entry2")
        self.plugin_file = os.path.join(pluginfolder, "DateTime.config")
        dt_file = open(self.plugin_file, "r")
        self.lines = ''.join(dt_file.readlines())
        old_date_format = re.search("date_format\s*=\s*(.*)\s*", self.lines).group(1)
        old_time_format = re.search("time_format\s*=\s*(.*)\s*", self.lines).group(1)
        self.date.set_text(old_date_format)
        self.time.set_text(old_time_format)

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        self.lines = re.sub("date_format\s*=\s*.*\s*", "date_format=" \
                     + self.date.get_text() + "\n", self.lines)
        self.lines = re.sub("time_format\s*=\s*.*\s*", "time_format=" \
                     + self.time.get_text() + "\n", self.lines)
        dt_file = open(self.plugin_file, "w")
        dt_file.write(self.lines)
        dt_file.close()
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
        gtk.main()
