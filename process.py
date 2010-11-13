# Now we need to process the files, nicely, please

import sys
from PIL import Image
import netCDF3
import numpy

hour = int(sys.argv[1])
job  = sys.argv[2]

def make_colorramp():
    """
    Make me a crude color ramp
    """
    c = numpy.zeros((256,3), numpy.int)
    
    # Ramp blue
    for b in range(0,37):
        c[b,2] = 255
    for b in range(37,77):
        c[b,2]= (77-b)*6
    for b in range(160,196):
        c[b,2]= (b-160)*6
    for b in range(196,256):
        c[b,2] = 254
    # Ramp Green up
    for g in range(0,37):
        c[g,1] = g*6
    for g in range(37,116):
        c[g,1] = 254
    for g in range(116,156):
        c[g,1] = (156-g)*6
    for g in range(196,256):
        c[g,1] = (g-196)*4
    # and Red
    for r in range(77,97):
        c[r,0] = (r-77)*12.
    for r in range(97,256):
        c[r,0] = 254

    c[0,:] = [0,0,0]
    return tuple( c.ravel() )

# Load up our tmpc surface data

nc = netCDF3.Dataset('data/ructemps.nc')
tmpc = nc.variables['tmpc'][hour,:,:]
nc.close()


# Load NET
netpng = Image.open("NET_%s.gif" % (job,))
net = (numpy.fromstring(netpng.tostring(), numpy.uint8)).reshape( (5200,12000))

# mask out the net based on temperature
net = numpy.where( tmpc > 3.0, net, 15)

# Load N0Q
n0qpng = Image.open("N0Q_%s.gif" % (job,))
n0q = (numpy.fromstring(n0qpng.tostring(), numpy.uint8)).reshape( (5200,12000))
#print numpy.min(n0q)
#print numpy.max(n0q)

# Clean n0q
n0q = numpy.where( net < 2, 0, n0q )

#for i in range(256):
#    n0q[i*10:i*10+10,0:100] = i

# Make the image, please!
png = Image.fromarray( n0q )
png.putpalette( make_colorramp() )
png.save('N0Q_CLEAN_%s.png' % (job,))
    