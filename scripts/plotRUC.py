import matplotlib.pyplot as plt
import netCDF4
import numpy

nc = netCDF4.Dataset("data/ructemps.nc")
data = nc.variables["tmpc"][17, :, :]
nc.close()

(fig, ax) = plt.subplots(1, 1)

ax.imshow(numpy.flipud(data))

fig.savefig("test.png")
