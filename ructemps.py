"""Merge Grib2 RAP temps into netcdf file."""
import os
import datetime
import sys
import tempfile

import requests
import numpy as np
from scipy import interpolate
import pygrib
from pyiem.util import ncopen, utc, logger
from metpy.units import units

LOG = logger()


def main(argv):
    """Go Main Go"""
    utcnow = utc()
    hr = 1 if len(argv) == 1 else int(argv[1])
    utcnow += datetime.timedelta(hours=hr)

    # Search for valid file
    grbs = None
    tmpk_2m = None
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        for fhour in range(10):
            ts = utcnow - datetime.timedelta(hours=fhour)
            uri = ts.strftime(
                "http://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/"
                f"model/rap/%H/rap.t%Hz.awp130f{fhour:03d}.grib2"
            )
            LOG.debug("requesting %s", uri)
            try:
                req = requests.get(uri, timeout=10)
                if req.status_code != 200:
                    LOG.debug("got status_code %s", req.status_code)
                    continue
                with open(tmpfd.name, "wb") as fh:
                    fh.write(req.content)
                grib = pygrib.open(tmpfd.name)
                grbs = grib.select(name="2 metre temperature")
                tmpk_2m = grbs[0].values
                lat, lon = grbs[0].latlons()
            except Exception as exp:
                LOG.debug(exp)
                continue
            if grbs:
                break
    os.unlink(tmpfd.name)

    if tmpk_2m is None:
        LOG.info("No data found for %s", utcnow)
        return

    with ncopen("data/ructemps.nc", "a") as nc:
        xx, yy = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])

        T = interpolate.griddata(
            (lon.ravel(), lat.ravel()),
            tmpk_2m.ravel(),
            (xx, yy),
            method="cubic",
        )
        data = nc.variables["tmpc"]
        writehr = utcnow.hour
        data[writehr, :, :] = (units("degK") * T).to(units("degC")).m


if __name__ == "__main__":
    main(sys.argv)
