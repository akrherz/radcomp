# Our hope is to get data valid for the next hour, so we'll try hard to do just that!
import numpy
import Nio
import os
import datetime
import pytz
import netCDF4
from scipy import interpolate

os.putenv('NCARG_ROOT', '/mesonet/local/ncarg')

utc = datetime.datetime.utcnow()
utc = utc.replace(tzinfo=pytz.timezone("UTC"))
# Look for F001 for this current hour!

# Search for valid file
for i in range(10):
    ts = utc - datetime.timedelta(hours=i)
    # rap.t02z.awp236pgrbf00.grib2
    fp = ts.strftime("/home/ldm/data/nccf/com/rap/prod/rap.%Y%m%d/rap.t%Hz.awp252pgrbf00.grib2")
    if os.path.isfile(fp):
        break

grib = Nio.open_file(fp, 'r')
lon =  grib.variables['gridlon_0'][:] 
lat = grib.variables['gridlat_0'][:] 
tmpk_2m = grib.variables['TMP_P0_L103_GLC0'][:]

x = numpy.arange(-126., -66., 0.05)
y = numpy.arange(24., 50., 0.05)
xx, yy = numpy.meshgrid(x,y)

T = interpolate.griddata((lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx,yy),
                         method='cubic')

nc = netCDF4.Dataset('data/ructemps.nc', 'a')
data = nc.variables['tmpc']
writehr = utc.hour 
#print 'Updated RUCTEMPS HR %s' % (writehr,)
data[writehr,:,:] = T - 273.15
nc.close()