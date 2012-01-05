#!/usr/bin/env python
# plugin GUI preferences class for LastfmPlayer
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re

class LastfmPlayer:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("LastfmPlayer.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.username = self.wTree.get_object("entry1")
        self.password = self.wTree.get_object("entry2")
        self.station = self.wTree.get_object("entry3")
        self.duration = self.wTree.get_object("entry4")
        self.password_file = os.path.join(os.environ['HOME'], '.shell-fm/shell-fm.rc')

        self.settingsblank = False
        if not os.path.exists(self.password_file):
            shell_fm_path = os.path.join(os.environ['HOME'], '.shell-fm')
            if not os.path.exists(shell_fm_path):
                os.mkdir(shell_fm_path)
            lfs_file = open(self.password_file, "w")
            lfs_file.close()
            
        lfs_file = open(self.password_file, "r")
        self.lines = ''.join(lfs_file.readlines())
        try:
            old_username = re.search("username\s*=\s*(.*)\s*password", self.lines).group(1)
            old_password = re.search("password\s*=\s*(.*)\s*", self.lines).group(1)
            old_station = re.search("default-radio=lastfm://(.*)\s*", self.lines).group(1)
            old_duration = re.search("#duration\s*=\s*(.*)\s*", self.lines).group(1)
        except:
            old_password = ""
            old_username = ""
            old_station = ""
            old_duration = ""
            self.settingsblank = True
        lfs_file.close()
        self.username.set_text(old_username)
        self.password.set_text(old_password)
        self.station.set_text(old_station)
        self.duration.set_text(old_duration)
            

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        if not self.settingsblank:
            self.lines = re.sub("username\s*=\s*.*\s*", "username=" \
                + self.username.get_text() + "\n", self.lines)
            self.lines = re.sub("password\s*=\s*.*\s*", "password=" \
                + self.password.get_text() + "\n", self.lines)
            self.lines = re.sub("default-radio=lastfm://(.*)\s*", \
                "default-radio=lastfm://" + self.station.get_text() + "\n", self.lines)
            self.lines = re.sub("#duration\s*=\s*.*\s*", "#duration=" \
                + self.duration.get_text() + "\n", self.lines)
        else:
            self.lines = "username=" + self.username.get_text() + "\n" \
                       + "password=" + self.password.get_text() + "\n" \
                       + "default-radio=lastfm://=" + self.station.get_text() + "\n" \
                       + "#duration=" + self.duration.get_text()
        
        lfs_file = open(self.password_file, "w")
        lfs_file.write(self.lines)
        lfs_file.close()
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
