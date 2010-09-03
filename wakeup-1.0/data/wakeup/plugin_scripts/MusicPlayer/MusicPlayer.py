#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import os
import re

class MusicPlayer:

    def __init__(self, pluginfolder):
        self.wTree = gtk.Builder()
        self.wTree.add_from_file("MusicPlayer.glade")
        self.window = self.wTree.get_object("window1")
        self.time = self.wTree.get_object("entry2")
        self.entry = self.wTree.get_object("entry1")
        self.plugin_file = os.path.join(pluginfolder, 'MusicPlayer.config')
        pl_file = open(self.plugin_file, "r")
        self.lines = ''.join(pl_file.readlines())
        pl_file.close()
        old_music_file = re.search("music_file\s*=[ \t]*([^\n]*)\s*", self.lines).group(1)
        self.entry.set_text(old_music_file)
        old_time = re.search("time\s*=\s*(.*)\s", self.lines).group(1)
        self.time.set_text(old_time)
        self.wTree.connect_signals(self)
        self.chooser = gtk.FileChooserDialog(title=None,
                            action=gtk.FILE_CHOOSER_ACTION_OPEN,
                            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.chooser.set_current_folder(os.environ['HOME'])
        if self.entry.get_text() != "":
            directory = re.search("(.*)/[^/]*", self.entry.get_text()).group(1)
            self.chooser.set_current_folder(directory)
        filter = gtk.FileFilter()
        filter.set_name("Audio files")
        filter.add_mime_type("audio/*")
        self.chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        self.chooser.add_filter(filter)

    '''On Clicking Open'''
    def on_open_clicked(self, widget, data=None):
        response = self.chooser.run()
        if response == gtk.RESPONSE_OK:
            self.entry.set_text(self.chooser.get_filename())
        self.chooser.hide()

    '''On Clicking Ok'''
    def on_ok_clicked(self, widget, data=None):
        if os.path.exists(self.entry.get_text()):
            self.lines = re.sub("music_file\s*=[ \t]*[^\n]*\s*", "music_file=" \
                + self.entry.get_text() + "\n", self.lines)
        t = self.time.get_text()
        match = re.search("(.*):(.*)", t)
        if t.isdigit() or (match and match.group(1).isdigit() and match.group(2).isdigit()):
            self.lines = re.sub("time\s*=\s*.*\s*", "time=" \
                + t + "\n", self.lines)
        pl_file = open(self.plugin_file, "w")
        pl_file.write(self.lines)
        pl_file.close()
        self.on_window_destroy(self)

    '''On Clicking Cancel'''
    def on_cancel_clicked(self, widget, data=None):
        self.on_window_destroy(self)

    '''Exit'''
    def on_window_destroy (self, widget, data=None):
        self.window.destroy()
        gtk.main_quit()

    '''Run the GUI'''
    def main(self):
        gtk.main()
