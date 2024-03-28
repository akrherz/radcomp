"""Generate World files"""

import datetime
import sys

from pyiem.util import get_dbconn, logger

LOG = logger()
WKT = {
    "US": "-126 50,-65 50,-65 23,-126 23,-126 50",
    "AK": "-170.5 68.71,-130.50 68.71,-130.50 53.21,-170.5 53.21,-170.5 68.71",
    "HI": (
        "-162.41 24.44,-152.41 24.44,-152.41 15.44,"
        "-162.41 15.44,-162.41 24.44"
    ),
    "PR": "-71.07 23.1,-61.07 23.1,-61.07 13.1,-71.07 13.01,-71.07 23.1",
    "GU": "140.5 17.7,149.0 17.7,149.0 9.2,140.5 9.2,140.5 17.7",
}
TFW = {
    "US": ["0.005", "0.0", "0.0", "-0.005", "-126.0", "50.0"],
    "AK": ["0.01", "0.0", "0.0", "-0.01", "-170.5", "68.71"],
    "HI": ["0.005", "0.0", "0.0", "-0.005", "-162.4", "24.44"],
    "PR": ["0.01", "0.0", "0.0", "-0.01", "-71.07", "23.1"],
    "GU": ["0.0085", "0.0", "0.0", "-0.0085", "140.5", "17.7"],
}

# Augh, database is tz naive
FMT = "%Y-%m-%d %H:%M"


def main(argv):
    """Go Main Go."""
    v = argv[1]
    sector = argv[2]
    sts = argv[3]
    ts = datetime.datetime.strptime(sts, "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=datetime.timezone.utc)
    LOG.info("parsed time: %s", ts)

    with open(f"{sector}_N0Q_CLEAN_{v}.tfw", "w", encoding="utf-8") as fh:
        fh.write("\n".join(TFW[sector]))

    mydb = get_dbconn("postgis")
    cursor = mydb.cursor()
    archivefn = ts.strftime(
        f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/{sector.lower()}comp/"
        "n0q_%Y%m%d%H%M.png"
    )
    LOG.info(archivefn)
    mywkt = f"SRID=4326;MULTIPOLYGON((({WKT[sector]})))"
    cursor.execute(
        "SELECT * from nexrad_n0q_tindex "
        "WHERE datetime = %s and filepath = %s",
        (ts.strftime(FMT), archivefn),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT into nexrad_n0q_tindex(the_geom, datetime, filepath) "
            "values (ST_GeomFromEWKT(%s), %s, %s)",
            (mywkt, ts.strftime(FMT), archivefn),
        )
    mydb.commit()
    mydb.close()


if __name__ == "__main__":
    main(sys.argv)
