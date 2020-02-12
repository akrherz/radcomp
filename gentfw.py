""" Generate World files """

import datetime
import sys

from pyiem.util import get_dbconn

v = sys.argv[1]
sector = sys.argv[2]
sts = sys.argv[3]
ts = datetime.datetime.strptime(sts, "%Y%m%d%H%M")


out = open("%s_N0Q_CLEAN_%s.tfw" % (sector, v), "w")

if sector == "US":
    wkt = "-126 50,-65 50,-65 23,-126 23,-126 50"
    out.write(
        """0.005
0.0
0.0
-0.005
-126.0
50.0"""
    )

elif sector == "AK":
    wkt = "-170.5 68.71,-130.50 68.71,-130.50 53.21,-170.5 53.21,-170.5 68.71"
    out.write(
        """0.01
0.0
0.0
-0.01
-170.5
68.71"""
    )

elif sector == "HI":
    wkt = "-162.41 24.44,-152.41 24.44,-152.41 15.44," "-162.41 15.44,-162.41 24.44"
    out.write(
        """0.005
0.0
 0.0
-0.005
-162.4
24.44"""
    )

elif sector == "PR":
    wkt = "-71.07 23.1,-61.07 23.1,-61.07 13.1,-71.07 13.01,-71.07 23.1"
    out.write(
        """0.01
0.0
0.0
-0.01
-71.07
23.1"""
    )

out.close()

mydb = get_dbconn("postgis")
cursor = mydb.cursor()
cursor.execute("SET TIME ZONE 'UTC'")
sql = """
    INSERT into nexrad_n0q_tindex( the_geom, datetime, filepath) values
    (ST_GeomFromEWKT('SRID=4326;MULTIPOLYGON(((%s)))'), '%s',
    '/mesonet/ARCHIVE/data/%s/GIS/%scomp/n0q_%s.png')
    """ % (
    wkt,
    ts.strftime("%Y-%m-%d %H:%M"),
    ts.strftime("%Y/%m/%d"),
    sector.lower(),
    ts.strftime("%Y%m%d%H%M"),
)
cursor.execute(sql)
mydb.commit()
mydb.close()
