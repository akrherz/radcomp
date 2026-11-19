"""Look for missing recent composites and run again!"""

import subprocess
from datetime import timedelta

from pyiem.util import archive_fetch, logger, utc

LOG = logger()


def main():
    """Go Main Go"""
    sts = utc()
    sts -= timedelta(hours=6)
    sts = sts.replace(minute=0, second=0, microsecond=0)
    ets = sts + timedelta(hours=1)
    interval = timedelta(minutes=5)

    now = sts
    while now < ets:
        ppath = now.strftime("%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png")
        LOG.info("Checking %s", ppath)
        with archive_fetch(ppath, method="head") as fh:
            if fh is None:
                LOG.warning("Processing %s", ppath)
                cmd = [
                    "/usr/bin/bash",
                    "n0r.sh",
                    f"{now:%Y}",
                    f"{now:%m}",
                    f"{now:%d}",
                    f"{now:%H}",
                    f"{now:%M}",
                    "n0r",
                    "1",
                ]
                subprocess.call(cmd)

        # Need to ensure all sectors exist so to keep tilecache happy
        for sector in ["US", "PR", "AK", "HI", "GU"]:
            ppath = now.strftime(
                f"%Y/%m/%d/GIS/{sector.lower()}comp/n0q_%Y%m%d%H%M.png"
            )
            LOG.info("Checking %s", ppath)
            with archive_fetch(ppath, method="head") as fh:
                if fh is None:
                    LOG.warning("Reprocess n0q: %s sector: %s", now, sector)
                    cmd = [
                        "/usr/bin/bash",
                        "production.sh",
                        sector,
                        f"{now:%Y}",
                        f"{now:%m}",
                        f"{now:%d}",
                        f"{now:%H}",
                        f"{now:%M}",
                        "OLD",
                    ]
                    subprocess.call(cmd)

        now += interval


if __name__ == "__main__":
    main()
