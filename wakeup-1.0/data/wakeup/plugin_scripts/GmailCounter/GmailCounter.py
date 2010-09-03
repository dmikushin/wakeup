#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re
import base64

class GmailCounter:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("GmailCounter.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.username = self.wTree.get_object("entry1")
        self.password = self.wTree.get_object("entry2")
        self.password_file = os.path.join(pluginfolder, 'GmailCounter.config')
        gs_file = open(self.password_file, "r")
        self.lines = ''.join(gs_file.readlines())
        old_username = re.search("username\s*=\s*(.*)\s*password", self.lines).group(1)
        old_password = re.search("password\s*=\s*(.*)\s*", self.lines).group(1)
        self.username.set_text(old_username)
        self.password.set_text(base64.b64decode(old_password))
        gs_file.close()

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        self.lines = re.sub("username\s*=\s*.*\s*", "username=" \
            + self.username.get_text() + "\n", self.lines)
        self.lines = re.sub("password\s*=\s*.*\s*", "password=" \
            + base64.b64encode(self.password.get_text()) + "\n", self.lines)
        gs_file = open(self.password_file, "w")
        gs_file.write(self.lines)
        gs_file.close()
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
