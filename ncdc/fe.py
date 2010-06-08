#!/usr/bin/python

import mx.DateTime, os

sts = mx.DateTime.DateTime(2002,10,1,0,0)
ets = mx.DateTime.DateTime(2002,12,1,0,0)
interval = mx.DateTime.RelativeDateTime(minutes=5)

now = sts
while (now < ets):
  print now
  if (now.hour == 0 and now.minute == 0):
    # Extract tomorrow
    cmd = "./extract.py %s" % (now.strftime("%Y %m %d"),)
    os.system(cmd)
  cmd = "./n0r-p2000.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
  os.system(cmd)
  if (now.hour == 23 and now.minute == 55):
    os.system("rm -rf /mesonet/data/nexrad/NIDS/*")
    os.system("rm -rf /mesonet/data/nexrad/incoming/nexrad3-herz")
    # reextract today :(
    cmd = "./extract.py %s" % (now.strftime("%Y %m %d"),)
    os.system(cmd)
  now += interval
