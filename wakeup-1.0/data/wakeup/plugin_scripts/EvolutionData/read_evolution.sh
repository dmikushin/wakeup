#!/bin/bash
$(dirname $0)/read_evolution.py $* | sed -r '/.*DEBUG.*/d' | sed -r ':a;N;$!ba;s/\n{3,}//g'
