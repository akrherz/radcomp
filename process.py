"""
  tmpc in the netcdf file is stored with 0,0 in lower left
  PIL will have imagery with 0,0 in upper left
"""

import sys
from PIL import Image
from PIL import PngImagePlugin
import netCDF4
import numpy as np
import datetime

hour = int(sys.argv[1])
job  = sys.argv[2]
sector = sys.argv[3]
netprod = sys.argv[4]

#print 'Looking for ructemps.nc hour: %s' % (hour,)

# Load EET
netpng = Image.open("%s_%s_%s.gif" % (sector, netprod, job))
sz = (netpng.size[1], netpng.size[0])
net = (np.fromstring(netpng.tobytes(), np.uint8)).reshape( sz )


if sector == "US":
    # Load up our tmpc surface data
    nc = netCDF4.Dataset('data/ructemps.nc')
    tmpc = nc.variables['tmpc'][hour,:,:]
    tmpc = np.flipud( tmpc )
    nc.close()
    
    # mask out the net based on temperature
    net = np.where( tmpc > 3.0, net, 15)
else:
    # No Filtering... for now
    net[:,:] = 15.

# Load N0Q
n0qpng = Image.open("%s_N0Q_%s.gif" % (sector, job))
n0q = (np.fromstring(n0qpng.tobytes(), np.uint8)).reshape( sz )

# Clean n0q
if netprod == 'EET':
    n0q = np.where( net < 10, 0, n0q )
else:
    n0q = np.where( net < 2, 0, n0q )    

#for i in range(256):
#    n0q[i*10:i*10+10,0:100] = i

# Make the image, please!
png = Image.fromarray( n0q )
#png.putpalette( make_colorramp() )
png.putpalette( n0qpng.getpalette() )
meta = PngImagePlugin.PngInfo()
meta.add_text('gentime', 
              datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
png.save('%s_N0Q_CLEAN_%s.png' % (sector, job), pnginfo=meta)
