import numpy, sys, Ngl, Nio, os
import mx.DateTime, shutil
import netCDF3

os.putenv('NCARG_ROOT', '/mesonet/local/ncarg')


# /mnt/mesonet/data/nccf/com/ruc/prod/ruc2a.20081111/ruc2.t03z.pgrb20anl.grib2

# Search for valid file
for i in range(10):
  ts = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(hours=i)
  fp = ts.strftime("/home/ldm/data/nccf/com/ruc/prod/ruc2a.%Y%m%d/ruc2.t%Hz.pgrb20f01.grib2")
  if (os.path.isfile(fp)):
    break

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
writehr = ts.hour + 1
if writehr == 24:
    writehr = 23
#print 'Updated RUCTEMPS HR %s' % (writehr,)
data[writehr,:,:] = T - 273.15
nc.close()