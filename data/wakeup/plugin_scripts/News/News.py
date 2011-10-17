#!/usr/bin/env python
# plugin GUI preferences class for News
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re

class News:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("News.glade")
        self.window = self.wTree.get_object("window1")
        self.wTree.connect_signals(self)
        self.rss_feed = self.wTree.get_object("entry1")
        self.num_max_feeds = self.wTree.get_object("spinbutton1")
        self.plugin_file = os.path.join(pluginfolder, 'News.config')
        rs_file = open(self.plugin_file, "r")
        self.lines = ''.join(rs_file.readlines())
        rs_file.close()
        try:
            old_rss_feed = re.search("rss_feed\s*=\s*(.*)\s*", self.lines).group(1)
            old_max_feeds = re.search("max_feeds\s*=\s*(.*)\s*", self.lines).group(1)
        except:
            old_rss_feed = ""
            old_max_feeds = 1
        self.rss_feed.set_text(old_rss_feed)
        self.num_max_feeds.set_value(float(old_max_feeds))

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        self.lines = re.sub("rss_feed\s*=( \t)*[^\n]*\n", "rss_feed=" \
            + self.rss_feed.get_text() + "\n", self.lines)
        self.lines = re.sub("max_feeds\s*=\s*.*\s*", "max_feeds=" \
            + str(self.num_max_feeds.get_value()) + "\n", self.lines)
        rs_file = open(self.plugin_file, "w")
        rs_file.write(self.lines)
        rs_file.close()
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
