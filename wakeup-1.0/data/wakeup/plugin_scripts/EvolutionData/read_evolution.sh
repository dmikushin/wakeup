#!/bin/bash
# wrapper for read_evolution.py that removes unwanted DEBUG and newlines
# Copyright (C) 2011 David Glass <dsglass@gmail.com>
# Copyright is GPLv3 or later, see /usr/share/common-licenses/GPL-3

$(dirname $0)/read_evolution.py $* 2>/dev/null | sed -r '/.*DEBUG.*/d' | sed -r ':a;N;$!ba;s/\n{3,}//g'
