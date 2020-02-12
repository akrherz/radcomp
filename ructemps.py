"""Merge Grib2 RAP temps into netcdf file."""
from __future__ import print_function
import os
import datetime
import sys

import numpy as np
import pytz
import netCDF4
from scipy import interpolate
import pygrib
from pyiem.datatypes import temperature


def main(argv):
    """Go Main Go"""
    utc = datetime.datetime.utcnow()
    hr = 1 if len(argv) == 1 else int(argv[1])
    utc = utc + datetime.timedelta(hours=hr)
    utc = utc.replace(tzinfo=pytz.UTC)

    # Search for valid file
    grbs = None
    for fhour in range(10):
        ts = utc - datetime.timedelta(hours=fhour)
        fstr = "%03i" % (fhour,)
        fn = ts.strftime(
            (
                "/mesonet/ARCHIVE/data/%Y/%m/%d/model/rap/"
                "%H/rap.t%Hz.awp130f" + fstr + ".grib2"
            )
        )
        if not os.path.isfile(fn):
            # print("Missing %s" % (fn, ))
            continue

        try:
            grib = pygrib.open(fn)
            grbs = grib.select(name="2 metre temperature")
        except Exception as exp:
            continue
        if grbs:
            break

    if grbs is None:
        print("Complete ructemps.py failure for %s" % (utc,))
        sys.exit()
    tmpk_2m = grbs[0].values
    lat, lon = grbs[0].latlons()

    nc = netCDF4.Dataset("data/ructemps.nc", "a")
    xx, yy = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])

    T = interpolate.griddata(
        (lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx, yy), method="cubic"
    )

    data = nc.variables["tmpc"]
    writehr = utc.hour
    data[writehr, :, :] = temperature(T, "K").value("C")
    nc.close()


if __name__ == "__main__":
    main(sys.argv)
