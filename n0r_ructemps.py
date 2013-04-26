#!/usr/bin/env python

import numpy
import Nio
import  os
import datetime
import pytz
import shutil
from osgeo import gdal, gdalconst
from scipy import interpolate

os.putenv('NCARG_ROOT', '/mesonet/local/ncarg')

utc = datetime.datetime.utcnow()
utc = utc + datetime.timedelta(hours=1)
utc = utc.replace(tzinfo=pytz.timezone("UTC"))

# Search for valid file
for i in range(10):
    ts = utc - datetime.timedelta(hours=i)
    # rap.t02z.awp236pgrbf00.grib2
    fp = ts.strftime("/mesonet/data/nccf/com/rap/prod/rap.%Y%m%d/rap.t%Hz.awp252pgrbf01.grib2")
    if os.path.isfile(fp):
        break

grib = Nio.open_file(fp, 'r')
lon = grib.variables['gridlon_0'][:]
lat = grib.variables['gridlat_0'][:]
tmpk_2m = grib.variables['TMP_P0_L103_GLC0'][:]

x = numpy.arange(-126., -66., 0.1)
y = numpy.arange(24., 50., 0.1)
xx, yy = numpy.meshgrid(x,y)

T = interpolate.griddata((lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx,yy),
                         method='cubic')

"""
import matplotlib.pyplot as plt
plt.subplot(111)
im = plt.imshow(T, extent=(0,1,1,0))
plt.colorbar(im)
plt.savefig('test.png')
"""

ifreezing = numpy.where( T < 279.0, 1., 0.)

n0r = gdal.Open('data/ifreeze.tif', 0)
n0rct = n0r.GetRasterBand(1).GetRasterColorTable()
n0rt = gdalconst.GDT_Byte

out_driver = n0r.GetDriver()
outdataset = out_driver.Create('data/ifreeze.tif', n0r.RasterXSize, n0r.RasterYSize, n0r.RasterCount, n0rt)
# Set output color table to match input
outdataset.GetRasterBand(1).SetRasterColorTable( n0rct )
outdataset.GetRasterBand(1).WriteArray( ifreezing )

# Force a cleanup, to make sure we close the output file
del outdataset
shutil.copyfile('data/ifreeze.tif', 'data/ifreeze%02i.tif' % (utc.hour,) )
