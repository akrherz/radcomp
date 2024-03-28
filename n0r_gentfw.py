"""Generate things."""

import datetime
import sys

from pyiem.util import get_dbconn, logger

LOG = logger()
# Augh, database is tz naive
FMT = "%Y-%m-%d %H:%M"


def main(argv):
    """Go Main Go."""
    v = argv[1]
    ts = datetime.datetime.strptime(v, "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=datetime.timezone.utc)

    with open(f"n0r{v}.tfw", "w", encoding="utf-8") as fh:
        fh.write("\n".join(["0.01", "0.0", "0.0", "-0.01", "-126.0", "50.0"]))

    if argv[2] != "n0r":
        return

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT * from nexrad_n0r_tindex WHERE datetime = %s",
        (ts.strftime(FMT),),
    )
    if cursor.rowcount == 0:
        archivefn = ts.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png"
        )
        LOG.info(archivefn)
        cursor.execute(
            "INSERT into nexrad_n0r_tindex (the_geom, datetime, filepath) "
            "values (GeomFromEWKT('SRID=4326; MULTIPOLYGON(((-126 50,-66 50,"
            "-66 24,-126 24,-126 50)))'), %s, %s)",
            (ts.strftime(FMT), archivefn),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
