#!/usr/bin/python

import mx.DateTime, os

sts = mx.DateTime.DateTime(2007, 10, 15, 0, 0)
ets = mx.DateTime.DateTime(2007, 10, 15, 3, 0)
interval = mx.DateTime.RelativeDateTime(minutes=5)

now = sts
while now < ets:
    print now
    cmd = "./n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
    os.system(cmd)
    now += interval
