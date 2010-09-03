#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re

class EvolutionData:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("EvolutionData.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.add_cal = self.wTree.get_object("entry1")
        self.cals_view = self.wTree.get_object("treeview1")
        self.cals_list = self.wTree.get_object("liststore1")
        self.plugin_file = os.path.join(pluginfolder, "EvolutionData.config")
        ed_file = open(self.plugin_file, "r")
        self.lines = ''.join(ed_file.readlines())
        exec("old_cals_list = [" + re.search("ignore_cals\s*=\s*\((.*)\)\s*", self.lines).group(1) + "]")
        for cal in old_cals_list:
            myiter = self.cals_list.append()
            self.cals_list.set_value(myiter, 0, cal)
        ed_file.close()

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        new_cals_list = '('
        item = self.cals_list.get_iter_first()
        if item:
            while item:
                if new_cals_list != "(":
                    new_cals_list += ", "
                new_cals_list += '"' + self.cals_list.get_value(item, 0) + '"'
                item = self.cals_list.iter_next(item)
        new_cals_list += ')'
        self.lines = re.sub("ignore_cals\\s*=\\s*.*\\s*", "ignore_cals=" \
            + new_cals_list + "\n", self.lines)
        ed_file = open(self.plugin_file, "w")
        ed_file.write(self.lines)
        ed_file.close()
        self.on_window_destroy(self)

    '''On Pressing Enter in the entry box'''
    def on_calendar_add(self, widget, data=None):
        if data.keyval == 65293: #if enter is pressed in the entry
            myiter = self.cals_list.append()
            self.cals_list.set_value(myiter, 0, widget.get_text())
            widget.set_text("")

    '''On pressing delete in the list'''
    def on_calendar_delete(self, widget, data=None):
        if data.keyval == 65535: # if delete is pressed
            entry1, entry2 = self.cals_view.get_selection().get_selected()
            self.cals_list.remove(entry2)


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
