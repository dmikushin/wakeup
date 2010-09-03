#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os

wakeup_folder = "/usr/share/wakeup/"


class StopAlarm:

    def __init__(self):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(os.path.join(wakeup_folder, "stopalarm.glade"))
        self.wTree.connect_signals(self)
        self.window = self.wTree.get_object("dialog1")
        self.minutes = self.wTree.get_object("adjustment2")
        self.hours = self.wTree.get_object("adjustment1")
        self.minutes.set_value(5.0)
        self.window.show_all()
        
    def on_alarm_stopped(self, widget, data=None):
        print 0
        gtk.main_quit()
        
    def on_alarm_snoozed(self, widget, data=None):
        hrs = self.hours.get_value()
        mins = self.minutes.get_value()
        print str(int(hrs*60 + mins))
        gtk.main_quit()

    '''Run the GUI'''
    def main(self):
        gtk.main()
        
        
'''Run the program'''
if __name__ == "__main__":
    stopalarm = StopAlarm()
    stopalarm.main()
