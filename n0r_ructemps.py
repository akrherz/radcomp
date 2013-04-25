#!/usr/bin/env python

import numpy, sys, Ngl, Nio, os
import mx.DateTime, shutil
from osgeo import gdal, gdalconst

os.putenv('NCARG_ROOT', '/mesonet/local/ncarg')

# /mnt/mesonet/data/nccf/com/ruc/prod/ruc2a.20081111/ruc2.t03z.pgrb20anl.grib2

# Search for valid file
for i in range(10):
  ts = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(hours=i)
  # rap.t02z.awp236pgrbf00.grib2
  fp = ts.strftime("/mesonet/data/nccf/com/rap/prod/rap.%Y%m%d/rap.t%Hz.awp236pgrbf00.grib2")
  if (os.path.isfile(fp)):
    break

grib = Nio.open_file(fp, 'r')
lon = numpy.ravel( grib.variables['gridlon_0'][:] )
lat = numpy.ravel( grib.variables['gridlat_0'][:] )
tmpk_2m = numpy.ravel( grib.variables['TMP_P0_L103_GLC0'][:] )
xgrid = numpy.arange(-126., -66., 0.25)
ygrid = numpy.arange(24., 50., 0.25)
res = Ngl.natgrid(lon[::3], lat[::3], tmpk_2m[::3], xgrid, ygrid)

T = numpy.zeros( (2600,6000), numpy.float32 )
(xl,yl) = numpy.shape( res )
for x in range(xl):
  for y in range(yl):
    T[ (y*25):((y+1)*25), (x*25):((x+1)*25) ] = res[x,yl-y-1]

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
shutil.copyfile('data/ifreeze.tif', 'data/ifreeze%02i.tif' % (ts.hour,) )
