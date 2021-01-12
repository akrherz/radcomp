"""Look for missing recent composites and run again!"""
import datetime
import os
import subprocess

# third party
import requests
from pyiem.util import utc, logger

LOG = logger()


def main():
    """Go Main Go"""
    sts = utc()
    sts -= datetime.timedelta(hours=6)
    sts = sts.replace(minute=0, second=0, microsecond=0)
    ets = sts + datetime.timedelta(hours=1)
    interval = datetime.timedelta(minutes=5)

    now = sts
    while now < ets:
        uri = now.strftime(
            "http://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/"
            "GIS/uscomp/n0r_%Y%m%d%H%M.png"
        )
        req = requests.get(uri, timeout=10)
        if req.status_code != 200:
            LOG.info("Reprocess n0r: %s", now)
            cmd = "csh n0r.csh %s n0r 1" % (now.strftime("%Y %m %d %H %M"),)
            subprocess.call(cmd, shell=True)

        uri = now.strftime(
            "http://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/"
            "GIS/uscomp/n0q_%Y%m%d%H%M.png"
        )
        req = requests.get(uri, timeout=10)
        if req.status_code != 200:
            LOG.info("Reprocess n0q: %s", now)
            for sector in ["US", "PR", "AK", "HI"]:
                cmd = ("sh production.sh %s %s OLD") % (
                    sector,
                    now.strftime("%Y %m %d %H %M"),
                )
                os.system(cmd)

        now += interval


if __name__ == "__main__":
    main()
