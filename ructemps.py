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

grib = Nio.open_file(fn, 'r')
lon =  grib.variables['gridlon_0'][:] 
lat = grib.variables['gridlat_0'][:] 
tmpk_2m = grib.variables['TMP_P0_L103_GLC0'][:]

x = numpy.arange(-126., -66., 0.005)
y = numpy.arange(24., 50., 0.005)
xx, yy = numpy.meshgrid(x,y)

T = interpolate.griddata((lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx,yy),
                         method='cubic')

nc = netCDF4.Dataset('data/ructemps.nc', 'a')
data = nc.variables['tmpc']
writehr = utc.hour 
#print 'Updated RUCTEMPS HR %s' % (writehr,)
data[writehr,:,:] = T - 273.15
nc.close()