"""
Proctor the reprocessing of NEXRAD data provide to me by NCDC
"""

import datetime
import subprocess

from pyiem.util import utc

sts = utc(2003, 1, 1)
ets = utc(2003, 2, 1)
interval = datetime.timedelta(minutes=5)

now = sts
while now < ets:
    print(now)
    if now.hour == 0 and now.minute == 0:
        # Extract tomorrow
        cmd = "python extract.py %s" % (now.strftime("%Y %m %d"),)
        subprocess.call(cmd, shell=True)

    cmd = "csh n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
    subprocess.call(cmd, shell=True)
    if now.hour == 23 and now.minute == 55:
        subprocess.call("rm -rf /tmp/nexrad/NIDS/*", shell=True)
        subprocess.call("rm -rf /tmp/nexrad3-herz", shell=True)
        # reextract today :(
        cmd = "python extract.py %s" % (now.strftime("%Y %m %d"),)
        subprocess.call(cmd, shell=True)
    now += interval
