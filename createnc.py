"""
 Bootstrap to setup the netcdf data file that will hold our
 RUC temperature analysis for later use by our gridders
"""

import netCDF4
import numpy

nc = netCDF4.Dataset('data/ructemps.nc', 'w')
nc.createDimension('x', 12000)
nc.createDimension('y', 5200)
nc.createDimension('hour', 24)

data = nc.createVariable('tmpc', numpy.int8, ('hour','y','x') )
data.long_name = '2m Temperature'
data.units = 'Celsius'

nc.close()