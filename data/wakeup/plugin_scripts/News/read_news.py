#!/usr/bin/env python
# plugin script for News outputting news items from an rss feed
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import feedparser
import re
import sys
import os

plugin_file = '/home/' + sys.argv[1] + '/.wakeup/' + os.environ['ALARM'] + \
              '/plugins/News/News.config'
rs_file = open(plugin_file, "r")
lines = ''.join(rs_file.readlines())
rss_url = re.search("rss_feed\s*=\s*(.*)\s*", lines).group(1)
max_feeds = int(float(re.search("max_feeds\s*=\s*(.*)\s*", lines).group(1)))

feed = feedparser.parse(rss_url)
j = 1;
for i in feed.entries:
    print i.title + ". ",
    if j >= max_feeds:
        break
    j = j + 1

