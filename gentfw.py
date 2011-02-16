#!/usr/bin/env python

import time, mx.DateTime, sys, pg, random

v = sys.argv[1]
sector = sys.argv[2]


out = open("%s_%s.tfw" % (sector, v), 'w')

if sector == 'US':
    out.write("""   0.0050000000000%s
   0.00000
   0.00000
  -0.005000000000000%s
-126.000000
  50.0000""" % (v, random.randint(0,1000) ) )
elif sector == 'AK':
    out.write("""   0.010000000000%s
   0.00000
   0.00000
  -0.01000000000000%s
-170.500000
  68.7100""" % (v, random.randint(0,1000) ) )
    
elif sector == 'HI': 
    out.write("""   0.005000000000%s
   0.00000
   0.00000
  -0.00500000000000%s
-162.400000
  24.4400""" % (v, random.randint(0,1000) ) )

out.close()

sys.exit(0)

mydb = pg.connect('postgis', 'iemdb')
mydb.query("SET TIME ZONE 'GMT'")
sql = "SELECT * from nexrad_n0r_tindex WHERE datetime = '%s'" % \
  (ts.strftime("%Y-%m-%d %H:%M"), )
sql2 = "INSERT into nexrad_n0r_tindex( the_geom, datetime, filepath) values \
  ('SRID=4326;MULTIPOLYGON(((-126 50,-66 50,-66 24,-126 24,-126 50)))', '%s', '/mesonet/ARCHIVE/data/%s/GIS/uscomp/n0r_%s.png')" % (ts.strftime("%Y-%m-%d %H:%M"), ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H%M") )
rs = mydb.query(sql).dictresult()
if len(rs) == 0:
  mydb.query(sql2)
