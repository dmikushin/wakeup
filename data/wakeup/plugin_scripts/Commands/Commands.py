#!/usr/bin/env python
# plugin GUI preferences class for Commands
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re


class Commands:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("Commands.glade")
        self.wTree.connect_signals(self)
        self.window = self.wTree.get_object("window1")
        self.item_entry = self.wTree.get_object("entry1")
        self.command_entry = self.wTree.get_object("entry2")
        self.command_list = self.wTree.get_object("liststore1")
        self.selection = self.wTree.get_object("treeview-selection1")
        self.remove_button = self.wTree.get_object("toolbutton2")
        self.plugin_file = os.path.join(pluginfolder, "Commands.config")
        c_file = open(self.plugin_file, "r")
        self.lines = ''.join(c_file.readlines())
        c_file.close()
        old_items = re.search("dataitems=(.*)", self.lines).group(1).split(",")
        old_commands = re.search("scripts=(.*)", self.lines).group(1).split(",")
        for i in xrange(len(old_items)):
            myiter = self.command_list.insert_after(None, None)
            self.command_list.set_value(myiter, 0, '$'+old_items[i])
            self.command_list.set_value(myiter, 1, old_commands[i])
        # Select first item in list
        self.selection.select_path(self.command_list.get_path(self.command_list.get_iter_first()))
        if old_items == ['']:
            old_items = []
            old_command = []
            self.on_remove_clicked(self.remove_button)

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        new_item_list = ''
        new_command_list = ''
        item = self.command_list.get_iter_first()
        dataitems = {}
        if item:
            while item:
                if self.command_list.get_value(item, 0)[1:] in dataitems:
                    self.selection.select_path(self.command_list.get_path(item))
                    self.item_entry.set_text(self.item_entry.get_text() + 'NamesMustBeUnique')
                    return
                else:
                    dataitems[self.command_list.get_value(item, 0)[1:]]=True
                comma = ','
                if new_item_list == '':
                    comma = ''
                new_item_list = self.command_list.get_value(item, 0)[1:] + comma + new_item_list
                new_command_list = self.command_list.get_value(item, 1) + comma + new_command_list
                item = self.command_list.iter_next(item)
        self.lines = "dataitems=" + new_item_list + "\nscripts=" + new_command_list
        c_file = open(self.plugin_file, "w")
        c_file.write(self.lines)
        c_file.close()
        self.on_window_destroy(self)

    '''On Clicking Add'''
    def on_add_clicked(self, widget, data=None):
        myiter = self.command_list.append()
        self.command_list.set_value(myiter, 0, '$newitem')
        self.command_list.set_value(myiter, 1, 'echo "newitem"')
        self.selection.select_path(self.command_list.get_path(myiter))
        self.item_entry.set_sensitive(True)
        self.command_entry.set_sensitive(True)
        self.remove_button.set_sensitive(True)

    '''On pressing delete in the list'''
    def on_remove_clicked(self, widget, data=None):
        model, paths = self.selection.get_selected_rows()
        position_selected = self.command_list.get_iter_from_string(str(paths[0][0]))
        pos = self.command_list.get_path(position_selected)[0]
        if pos == 0:
            newpos = (1,)
        else:
            newpos = (pos-1,)
        self.selection.select_path(newpos)
        self.command_list.remove(position_selected)

    '''On Changing the item entry'''
    def on_itementry_changed(self, widget, data=None):
        model, paths = self.selection.get_selected_rows()
        try:
            position_selected = self.command_list.get_iter_from_string(str(paths[0][0]))
        except: # setting to blank in exception in on_selection_changed
            return
        self.command_list.set_value(position_selected, 0, '$'+widget.get_text())

    '''On Changing the command entry'''
    def on_commandentry_changed(self, widget, data=None):
        model, paths = self.selection.get_selected_rows()
        try:
            position_selected = self.command_list.get_iter_from_string(str(paths[0][0]))
        except: # setting to blank in exception in on_selection_changed
            return
        self.command_list.set_value(position_selected, 1, widget.get_text())

    '''On changing selection in command list'''
    def on_selection_changed(self, widget, data=None):
        model, paths = self.selection.get_selected_rows()
        try:
            position_selected = self.command_list.get_iter_from_string(str(paths[0][0]))
        except: # empty list
            self.item_entry.set_text("")
            self.command_entry.set_text("")
            self.item_entry.set_sensitive(False)
            self.command_entry.set_sensitive(False)
            self.remove_button.set_sensitive(False)
            return
        dataitem = self.command_list.get_value(position_selected, 0)
        command = self.command_list.get_value(position_selected, 1)
        self.item_entry.set_text(dataitem[1:])
        self.command_entry.set_text(command)

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
