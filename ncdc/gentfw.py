import random
import sys

import mx.DateTime
import pg

v = sys.argv[1]
ts = mx.DateTime.strptime(v, "%Y%m%d%H%M")

out = open("n0r%s.tfw" % (v,), "w")

out.write(
    """   0.0100000000000%s
   0.00000
   0.00000
  -0.010000000000000%s
-126.000000
  50.0000"""
    % (v, random.randint(0, 1000))
)

out.close()

sys.exit(0)

mydb = pg.connect("postgis", "iemdb-postgis.local")
mydb.query("SET TIME ZONE 'GMT'")
sql = "SELECT * from nexrad_n0r_tindex WHERE datetime = '%s'" % (
    ts.strftime("%Y-%m-%d %H:%M"),
)
sql2 = (
    "INSERT into nexrad_n0r_tindex( the_geom, datetime, filepath) values \
  ('SRID=4326;MULTIPOLYGON(((-126 50,-66 50,-66 24,-126 24,-126 50)))', \
    '%s', '/mesonet/ARCHIVE/data/%s/GIS/uscomp/n0r_%s.png')"
    % (
        ts.strftime("%Y-%m-%d %H:%M"),
        ts.strftime("%Y/%m/%d"),
        ts.strftime("%Y%m%d%H%M"),
    )
)
rs = mydb.query(sql).dictresult()
if len(rs) == 0:
    mydb.query(sql2)
