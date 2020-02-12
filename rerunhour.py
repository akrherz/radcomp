"""Look for missing recent composites and run again!"""
from __future__ import print_function
import datetime
import os
import subprocess


def main():
    """Go Main Go"""
    sts = datetime.datetime.utcnow()
    sts -= datetime.timedelta(hours=6)
    sts = sts.replace(minute=0, second=0, microsecond=0)
    ets = sts + datetime.timedelta(hours=1)
    interval = datetime.timedelta(minutes=5)

    now = sts
    while now < ets:
        fn = now.strftime(
            ("/mesonet/ARCHIVE/data/%Y/%m/%d/" "GIS/uscomp/n0r_%Y%m%d%H%M.png")
        )
        if not os.path.isfile(fn):
            print("Reprocess n0r: %s" % (fn,))
            cmd = "csh n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
            subprocess.call(cmd, shell=True)

        fn = now.strftime(
            ("/mesonet/ARCHIVE/data/%Y/%m/%d/" "GIS/uscomp/n0q_%Y%m%d%H%M.png")
        )
        if not os.path.isfile(fn):
            print("Reprocess n0q: %s" % (fn,))
            for sector in ["US", "PR", "AK", "HI"]:
                cmd = ("sh production.sh %s %s OLD") % (
                    sector,
                    now.strftime("%Y %m %d %H %M"),
                )
                os.system(cmd)

        now += interval


if __name__ == "__main__":
    main()
