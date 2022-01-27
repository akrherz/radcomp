"""
 Use the RAP model to provide a mask for use in clutter suppression by
 the NEXRAD compositer
"""
import os
import datetime
import warnings
import tempfile

import numpy as np
from osgeo import gdal, gdalconst
import requests
from pyiem.util import utc, logger
from scipy import interpolate
import pygrib

LOG = logger()

# n0r_ructemps.py:55: RuntimeWarning: invalid value encountered in less
#  ifreezing = np.where( T < 279.0, 1., 0.)
warnings.simplefilter("ignore", RuntimeWarning)


def main():
    """Run for a valid timestamp"""
    utcnow = utc()
    utcnow += datetime.timedelta(hours=1)

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
            LOG.info("requesting %s", uri)
            try:
                req = requests.get(uri, timeout=10)
                if req.status_code != 200:
                    LOG.info("got status_code %s", req.status_code)
                    continue
                with open(tmpfd.name, "wb") as fh:
                    fh.write(req.content)
                grib = pygrib.open(tmpfd.name)
                grbs = grib.select(name="2 metre temperature")
                tmpk_2m = grbs[0].values
                lat, lon = grbs[0].latlons()
            except Exception as exp:
                os.unlink(tmpfd.name)
                LOG.info(exp)
                continue
            if grbs:
                break
    os.unlink(tmpfd.name)

    if tmpk_2m is None:
        LOG.info("No data found for %s", utcnow)
        return

    x = np.arange(-126.0, -66.0, 0.01)
    y = np.arange(24.0, 50.0, 0.01)
    xx, yy = np.meshgrid(x, y)

    T = interpolate.griddata(
        (lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx, yy), method="cubic"
    )
    T = np.flipud(T)

    # Anything less than 6 C we will not consider for masking
    ifreezing = np.where(T < 279.0, 1.0, 0.0)

    n0rct = gdal.ColorTable()
    n0rct.SetColorEntry(0, (0, 0, 0))
    n0rct.SetColorEntry(1, (255, 0, 0))

    out_driver = gdal.GetDriverByName("GTiff")
    outfn = f"data/ifreeze-{utcnow:%Y%m%d%H}.tif"
    outdataset = out_driver.Create(outfn, 6000, 2600, 1, gdalconst.GDT_Byte)
    # Set output color table to match input
    outdataset.GetRasterBand(1).SetRasterColorTable(n0rct)
    outdataset.GetRasterBand(1).WriteArray(ifreezing)


if __name__ == "__main__":
    main()
