"""Run timestamps over again."""

import subprocess
import sys
import datetime


def main(argv):
    """Go Main Go."""
    sts = datetime.datetime(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5])
    )
    ets = datetime.datetime(
        int(argv[6]), int(argv[7]), int(argv[8]), int(argv[9]), int(argv[10])
    )
    interval = datetime.timedelta(minutes=5)

    now = sts
    while now < ets:
        print(now)
        dt = now.strftime("%Y %m %d %H %M")
        cmd = "csh n0r.csh %s n0r 1" % (dt,)
        subprocess.call(cmd, shell=True)
        for sector in ["PR", "US", "AK", "HI"]:
            cmd = "sh production.sh %s %s A" % (sector, dt)
            subprocess.call(cmd, shell=True)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
