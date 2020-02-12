"""Generate things."""
import datetime
import sys

from pyiem.util import get_dbconn

v = sys.argv[1]
ts = datetime.datetime.strptime(v, "%Y%m%d%H%M")

with open("n0r%s.tfw" % (v,), "w") as fh:
    fh.write(
        """0.01
0.0
0.0
-0.01
-126.0
50.0"""
    )

if sys.argv[2] != "n0r":
    sys.exit(0)

pgconn = get_dbconn("postgis")
cursor = pgconn.cursor()
sql = """SELECT * from nexrad_n0r_tindex WHERE datetime = '%s'
    """ % (
    ts.strftime("%Y-%m-%d %H:%M+00"),
)
sql2 = """INSERT into nexrad_n0r_tindex
    (the_geom, datetime, filepath) values
 (GeomFromEWKT('SRID=4326;
  MULTIPOLYGON(((-126 50,-66 50,-66 24,-126 24,-126 50)))'),
    '%s', '/mesonet/ARCHIVE/data/%s/GIS/uscomp/n0r_%s.png')
""" % (
    ts.strftime("%Y-%m-%d %H:%M"),
    ts.strftime("%Y/%m/%d"),
    ts.strftime("%Y%m%d%H%M"),
)
cursor.execute(sql)
if cursor.rowcount == 0:
    cursor.execute(sql2)

cursor.close()
pgconn.commit()
