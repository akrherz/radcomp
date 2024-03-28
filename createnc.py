"""
Bootstrap to setup the netcdf data file that will hold our
RUC temperature analysis for later use by our gridders
"""

import netCDF4
import numpy as np


def main():
    """Go Main Go"""
    nc = netCDF4.Dataset("data/ructemps.nc", "w")
    nc.createDimension("lon", 12200)
    nc.createDimension("lat", 5400)
    nc.createDimension("hour", 24)

    data = nc.createVariable("tmpc", np.int8, ("hour", "lat", "lon"))
    data.long_name = "2m Temperature"
    data.units = "Celsius"

    lat = nc.createVariable("lat", float, ("lat"))
    lat.long_name = "Latitude"
    lat[:] = np.arange(23.0, 50.0, 0.005)

    lon = nc.createVariable("lon", float, ("lon"))
    lon.long_name = "Longitude"
    lon[:] = np.arange(-126.0, -65.0, 0.005)

    nc.close()


if __name__ == "__main__":
    main()
