"""Run timestamps over again."""

import datetime
import subprocess
import sys

from pyiem.util import logger

LOG = logger()


def main(argv):
    """Go Main Go."""
    sts = datetime.datetime(*[int(x) for x in argv[1:6]])
    ets = datetime.datetime(*[int(x) for x in argv[6:11]])
    interval = datetime.timedelta(minutes=5)

    now = sts
    while now < ets:
        LOG.info(now)
        dt = now.strftime("%Y %m %d %H %M")
        for sector in ["PR", "US", "AK", "HI", "GU"]:
            cmd = f"sh production.sh {sector} {dt} A"
            subprocess.call(cmd, shell=True)
        # N0R is generated off of N0Q
        cmd = f"csh n0r.csh {dt} n0r 1"
        subprocess.call(cmd, shell=True)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
