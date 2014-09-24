"""
 Use the RAP model to provide a mask for use in clutter suppression by 
 the NEXRAD compositer
"""

import numpy as np
import pygrib
import  os
import sys
import datetime
import pytz
import shutil
from osgeo import gdal, gdalconst
from scipy import interpolate
import warnings
# n0r_ructemps.py:55: RuntimeWarning: invalid value encountered in less
#  ifreezing = np.where( T < 279.0, 1., 0.)
warnings.simplefilter("ignore", RuntimeWarning)

os.putenv('NCARG_ROOT', '/mesonet/local/ncarg')

utc = datetime.datetime.utcnow()
utc = utc + datetime.timedelta(hours=1)
utc = utc.replace(tzinfo=pytz.timezone("UTC"))

# Search for valid file
for fhour in range(10):
    ts = utc - datetime.timedelta(hours=fhour)
    fstr = "%03i" % (fhour,)
    fn = ts.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/model/rap/"+
                     "%H/rap.t%Hz.awp130f"+fstr+".grib2")
    if os.path.isfile(fn):
        break

grib = pygrib.open(fn)
grbs = grib.select(name='2 metre temperature')
if len(grbs) == 0:
    print 'Could not find 2m Temperature! %s' % (fn,)
    sys.exit()
tmpk_2m = grbs[0].values
lat, lon = grbs[0].latlons()

x = np.arange(-126., -66., 0.01)
y = np.arange(24., 50., 0.01)
xx, yy = np.meshgrid(x,y)

T = interpolate.griddata((lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx,yy),
                         method='cubic')
T = np.flipud(T)

"""
import matplotlib.pyplot as plt
plt.subplot(111)
im = plt.imshow(T, extent=(0,1,1,0))
plt.colorbar(im)
plt.savefig('test.png')
"""

ifreezing = np.where( T < 279.0, 1., 0.)

n0r = gdal.Open('data/ifreeze.tif', 0)
n0rct = gdal.ColorTable()
n0rct.SetColorEntry(0, (0,0,0))
n0rct.SetColorEntry(1, (255,0,0))
#n0rct = n0r.GetRasterBand(1).GetRasterColorTable()
n0rt = gdalconst.GDT_Byte

out_driver = n0r.GetDriver()
outdataset = out_driver.Create('data/ifreeze.tif', n0r.RasterXSize, n0r.RasterYSize, n0r.RasterCount, n0rt)
# Set output color table to match input
outdataset.GetRasterBand(1).SetRasterColorTable( n0rct )
outdataset.GetRasterBand(1).WriteArray( ifreezing )

# Force a cleanup, to make sure we close the output file
del outdataset
shutil.copyfile('data/ifreeze.tif', 'data/ifreeze%02i.tif' % (utc.hour,) )
