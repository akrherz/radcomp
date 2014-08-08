# Our hope is to get data valid for the next hour, so we'll try hard to do just that!
import numpy as np
import pygrib
import os
import datetime
import pytz
import netCDF4
import sys
from scipy import interpolate

utc = datetime.datetime.utcnow()
hr = 1 if len(sys.argv) == 1 else int(sys.argv[1])
utc = utc + datetime.timedelta(hours=hr)
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

nc = netCDF4.Dataset('data/ructemps.nc', 'a')
xx, yy = np.meshgrid(nc.variables['lon'][:], nc.variables['lat'][:])

T = interpolate.griddata((lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx,yy),
                         method='cubic')

data = nc.variables['tmpc']
writehr = utc.hour 
#print 'Updated RUCTEMPS HR %s' % (writehr,)
data[writehr,:,:] = T - 273.15
nc.close()