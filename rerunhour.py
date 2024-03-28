"""Look for missing recent composites and run again!"""

import datetime
import subprocess

# third party
import requests
from pyiem.util import logger, utc

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
            cmd = f"csh n0r.csh {now:%Y %m %d %H %M} n0r 1"
            subprocess.call(cmd, shell=True)

        # Need to ensure all sectors exist so to keep tilecache happy
        for sector in ["US", "PR", "AK", "HI", "GU"]:
            uri = now.strftime(
                "http://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/"
                f"GIS/{sector.lower()}comp/n0q_%Y%m%d%H%M.png"
            )
            req = requests.get(uri, timeout=10)
            if req.status_code != 200:
                LOG.info("Reprocess n0q: %s sector: %s", now, sector)
                cmd = f"sh production.sh {sector} {now:%Y %m %d %H %M} OLD"
                subprocess.call(cmd, shell=True)

        now += interval


if __name__ == "__main__":
    main()
