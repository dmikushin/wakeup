#!/usr/bin/env python
# A separate file is needed to create the boot alarms playfile with root permissions pre-writing.
# This script provides that file. Should be run as root.
# Copyright (C) 2012 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

import sys, os, stat
text = ''.join(sys.stdin.readlines())
filename = sys.argv[1]


# opens as 644 (group and others can only read, owner can't execute)
f = open(filename, 'w')
f.write(text)
f.close()

# changes permissions to 700 (add execute to owner, remove read from all others)
os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR)
