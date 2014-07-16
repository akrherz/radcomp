"""
  tmpc in the netcdf file is stored with 0,0 in lower left
  PIL will have imagery with 0,0 in upper left
"""

import sys
from PIL import Image
import netCDF4
import numpy

hour = int(sys.argv[1])
job  = sys.argv[2]
sector = sys.argv[3]

if sector == "US":
    # Load up our tmpc surface data
    nc = netCDF4.Dataset('data/ructemps.nc')
    tmpc = nc.variables['tmpc'][hour,:,:]
    tmpc = numpy.flipud( tmpc )
    nc.close()
    sz = (5200,12000)
elif sector == 'AK':
    sz = (1550,4000)
    
elif sector == 'HI':
    sz = (1800,2000)
    

# Load NET
netpng = Image.open("%s_EET_%s.gif" % (sector, job))
net = (numpy.fromstring(netpng.tobytes(), numpy.uint8)).reshape( sz )

if sector == 'US':
    # mask out the net based on temperature
    net = numpy.where( tmpc > 3.0, net, 15)
else:
    # No Filtering... for now
    net[:,:] = 15.

# Load N0Q
n0qpng = Image.open("%s_N0Q_%s.gif" % (sector, job))
n0q = (numpy.fromstring(n0qpng.tobytes(), numpy.uint8)).reshape( sz )

# Clean n0q
n0q = numpy.where( net < 10, 0, n0q )

#for i in range(256):
#    n0q[i*10:i*10+10,0:100] = i

# Make the image, please!
png = Image.fromarray( n0q )
#png.putpalette( make_colorramp() )
png.putpalette( n0qpng.getpalette() )
png.save('%s_N0Q_CLEAN_%s.png' % (sector, job))