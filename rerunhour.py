#!/usr/bin/python

import mx.DateTime
import os

now = mx.DateTime.gmt()
sts = now - mx.DateTime.RelativeDateTime(hours=6,minute=0)
ets = sts + mx.DateTime.RelativeDateTime(hours=1)
interval = mx.DateTime.RelativeDateTime(minutes=5)


now = sts
while (now < ets):
  fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png")
  if not os.path.isfile(fp):
    print 'Reprocess n0r:', fp
    cmd = "./n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
    os.system(cmd)
  now += interval

