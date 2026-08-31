"""Run timestamps over again."""

import subprocess
import sys
from datetime import datetime, timedelta

from pyiem.util import logger

LOG = logger()


def main(argv):
    """Go Main Go."""
    sts = datetime(*[int(x) for x in argv[1:6]])
    ets = datetime(*[int(x) for x in argv[6:11]])
    interval = timedelta(minutes=5)

    now = sts
    while now < ets:
        LOG.info(now)
        dt = now.strftime("%Y %m %d %H %M")
        for sector in ["PR", "US", "AK", "HI", "GU"]:
            cmd = ["bash", "production.sh", sector, *dt.split(), "A"]
            subprocess.call(cmd)
        # N0R is generated off of N0Q
        cmd = ["bash", "n0r.sh", *dt.split(), "n0r", "1"]
        subprocess.call(cmd)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
