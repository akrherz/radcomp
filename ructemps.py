# Our hope is to get data valid for the next hour, so we'll try hard to do just that!
import numpy, sys, Ngl, Nio, os
import mx.DateTime, shutil
import netCDF3

os.putenv('NCARG_ROOT', '/mesonet/local/ncarg')

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=1)
# Look for F001 for this current hour!
ts = mx.DateTime.gmt()
fp = ts.strftime("/home/ldm/data/nccf/com/rap/prod/rap.%Y%m%d/rap.t%Hz.awp252pgrbf01.grib2")
if not os.path.isfile(fp):
    # Look for F002 for the previous hour
    ts = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(hours=1)
    fp = ts.strftime("/home/ldm/data/nccf/com/rap/prod/rap.%Y%m%d/rap.t%Hz.awp252pgrbf01.grib2")
    if not os.path.isfile(fp):
        print "FAIL! Missing both RUC2 files"
        sys.exit()

grib = Nio.open_file(fp, 'r')
lon = numpy.ravel( grib.variables['gridlon_0'][:] )
lat = numpy.ravel( grib.variables['gridlat_0'][:] )
tmpk_2m = numpy.ravel( grib.variables['TMP_P0_L103_GLC0'][:] )
xgrid = numpy.arange(-126., -66., 0.25)
ygrid = numpy.arange(24., 50., 0.25)
res = Ngl.natgrid(lon[::3], lat[::3], tmpk_2m[::3], xgrid, ygrid)

T = numpy.zeros( (5200,12000), numpy.float32 )
(xl,yl) = numpy.shape( res )
for x in range(xl):
  for y in range(yl):
    T[ (y*50):((y+1)*50), (x*50):((x+1)*50) ] = res[x,yl-y-1]

nc = netCDF3.Dataset('data/ructemps.nc', 'a')
data = nc.variables['tmpc']
writehr = now.hour 
#print 'Updated RUCTEMPS HR %s' % (writehr,)
data[writehr,:,:] = T - 273.15
nc.close()