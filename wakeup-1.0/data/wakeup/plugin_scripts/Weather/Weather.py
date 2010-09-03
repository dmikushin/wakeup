#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re
import commands

class Weather:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("Weather.glade")
        self.window = self.wTree.get_object("window1")
#        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
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
        self.auto_location = commands.getoutput('''settings=$(gconftool-2 --get /apps/panel/applets/clock_screen0/prefs/cities) 
              echo $settings | grep -oP \"code=\\\"\\w*\\\" current=\\\"true\\"\" | grep -oP \"[A-Z]{4}\"''')
        self.temp_units.set_active(old_temp_units)
        self.wind_units.set_active(old_wind_units)
        if old_location == "none":
            self.manual_id.set_text(self.auto_location)
        else:
            self.manual_id.set_text(old_location)
        if not old_location == self.auto_location and not old_location == "none":
            self.manual_id.set_sensitive(False)
            self.set_manual.set_active(True)

    '''On Checking to set weather ID manually'''
    def on_manualID_toggled(self, widget, data=None):
        self.manual_id.set_sensitive(widget.get_active())

    '''On changing temperature units'''
    def on_tempUnits_changed(self, widget, data=None):
        pass

    '''On changing wind units'''
    def on_windUnits_changed(self, widget, data=None):
        pass

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
        gtk.main()
