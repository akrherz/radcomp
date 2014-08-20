"""
 This script checks our processing of N0R composites and reruns any missing
 composites 
"""

import datetime
import os
import subprocess

sts = datetime.datetime.utcnow()
sts -= datetime.timedelta(hours=6)
sts = sts.replace(minute=0,second=0,microsecond=0)
ets = sts + datetime.timedelta(hours=1)
interval = datetime.timedelta(minutes=5)


now = sts
while now < ets:
    fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/"
                       +"GIS/uscomp/n0r_%Y%m%d%H%M.png"))
    if not os.path.isfile(fn):
        print 'Reprocess n0r:', fn
        cmd = "csh n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
        subprocess.call(cmd, shell=True)
    now += interval

