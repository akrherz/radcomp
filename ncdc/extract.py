"""
Extract NCDC file into something we can feed to nex2img
"""

import datetime
import glob
import os
import subprocess
import sys

ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

os.chdir("/tmp/")
# Extract tar file
cmd = "tar -xf /mnt/mtarchive/data/nexrad3_archive/%s/N3_N0R_NET_%s.tar" % (
    ts.year,
    ts.strftime("%Y%m%d"),
)
os.system(cmd)
# unzip other files
os.chdir("nexrad3-herz/%s" % (ts.year,))

files = glob.glob("*%s*.zip" % (ts.strftime("%Y%m%d"),))
for fn in files:
    p = subprocess.Popen("unzip -o " + fn, shell=True, stdout=subprocess.PIPE)
    lines = p.stdout.readlines()
    for line in lines:
        if line.find("extracting:") == -1 and line.find("inflating:") == -1:
            continue
        l3 = line.split()[1]
        # KAKQ_SDUS51_N0RAKQ_200301010004
        nexrad = l3[15:18]
        typ = l3[12:15]
        yyyymmdd = l3[19:27]
        hhmm = l3[27:]
        nd = "/tmp/nexrad/NIDS/%s/%s" % (nexrad, typ)
        if not os.path.isdir(nd):
            os.makedirs(nd)
        nf = "%s_%s_%s" % (typ, yyyymmdd, hhmm)
        os.rename(l3, nd + "/" + nf)
    os.remove(fn)
