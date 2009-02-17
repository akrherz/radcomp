#!/usr/bin/python

import mx.DateTime, os

now = mx.DateTime.gmt()
sts = now - mx.DateTime.RelativeDateTime(hours=6,minute=0)
ets = sts + mx.DateTime.RelativeDateTime(hours=1)
interval = mx.DateTime.RelativeDateTime(minutes=5)


now = sts
while (now < ets):
  cmd = "./n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
  os.system(cmd)
  now += interval
