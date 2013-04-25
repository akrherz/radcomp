#!/usr/bin/env python

import numpy
import sys
import datetime
import pytz
from osgeo import gdal,  gdalconst

n = sys.argv[1]
ts = datetime.datetime.strptime(sys.argv[2], "%Y%m%d%H%M")
ts = ts.replace(tzinfo=pytz.timezone("UTC"))

# Open base reflectivity layer (n0r)
n0r = gdal.Open('n0r_%s_in.tif' % (n,), 0)
n0rct = n0r.GetRasterBand(1).GetRasterColorTable()
n0rd = n0r.ReadAsArray()
n0rt = gdalconst.GDT_Byte

fn = 'data/ifreeze%02i.tif' % (ts.hour,) 
ifreeze = gdal.Open(fn, 0)
ifr = ifreeze.ReadAsArray()

# Open net echo tops composite
net = gdal.Open('net_%s_in.tif' % (n,), 0)
# Winter mask for now
v = net.ReadAsArray()
#v[:,0:2400] = 10.
#v[:1300,2400:] = 10.

v = numpy.where( ifr > 0, 10., v)

# Do the comparison of n0r vs net
n0rd2 = numpy.where( v < 2. , 0, n0rd )

# Create output file
out_driver = n0r.GetDriver()
outdataset = out_driver.Create('n0r_%s_out.tif' % (n,), n0r.RasterXSize, n0r.RasterYSize, n0r.RasterCount, n0rt)
# Set output color table to match input
outdataset.GetRasterBand(1).SetRasterColorTable( n0rct )
outdataset.GetRasterBand(1).WriteArray( n0rd2 )

# Force a cleanup, to make sure we close the output file
del outdataset
