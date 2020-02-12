"""
 Use the RAP model to provide a mask for use in clutter suppression by
 the NEXRAD compositer
"""
from __future__ import print_function
import os
import sys
import datetime
import warnings

import numpy as np
import pytz
from osgeo import gdal, gdalconst
from scipy import interpolate
import pygrib

# n0r_ructemps.py:55: RuntimeWarning: invalid value encountered in less
#  ifreezing = np.where( T < 279.0, 1., 0.)
warnings.simplefilter("ignore", RuntimeWarning)


def run(utc):
    """Run for a valid timestamp"""
    grbs = None
    # Search for valid file
    for fhour in range(10):
        ts = utc - datetime.timedelta(hours=fhour)
        fstr = "%03i" % (fhour,)
        fn = ts.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/rap/"
            "%H/rap.t%Hz.awp130f" + fstr + ".grib2"
        )
        # print fn
        if not os.path.isfile(fn):
            continue
        try:
            grib = pygrib.open(fn)
            grbs = grib.select(name="2 metre temperature")
        except Exception as _exp:
            continue
        if grbs is not None:
            break
    if grbs is None:
        print("n0r_ructemps major failure! No data found for %s" % (utc,))
        return
    tmpk_2m = grbs[0].values
    lat, lon = grbs[0].latlons()

    x = np.arange(-126.0, -66.0, 0.01)
    y = np.arange(24.0, 50.0, 0.01)
    xx, yy = np.meshgrid(x, y)

    T = interpolate.griddata(
        (lon.ravel(), lat.ravel()), tmpk_2m.ravel(), (xx, yy), method="cubic"
    )
    T = np.flipud(T)

    """
    import matplotlib.pyplot as plt
    plt.subplot(111)
    im = plt.imshow(T, extent=(0,1,1,0))
    plt.colorbar(im)
    plt.savefig('test.png')
    """

    # Anything less than 6 C we will not consider for masking
    ifreezing = np.where(T < 279.0, 1.0, 0.0)

    n0rct = gdal.ColorTable()
    n0rct.SetColorEntry(0, (0, 0, 0))
    n0rct.SetColorEntry(1, (255, 0, 0))

    out_driver = gdal.GetDriverByName("GTiff")
    outfn = "data/ifreeze-%s.tif" % (utc.strftime("%Y%m%d%H"),)
    outdataset = out_driver.Create(outfn, 6000, 2600, 1, gdalconst.GDT_Byte)
    # Set output color table to match input
    outdataset.GetRasterBand(1).SetRasterColorTable(n0rct)
    outdataset.GetRasterBand(1).WriteArray(ifreezing)


def main(argv):
    """Go Main Go"""
    # Script runs at :58 after and we generate a file valid for the next hour
    utc = datetime.datetime.utcnow()
    utc = utc + datetime.timedelta(hours=1)
    utc = utc.replace(tzinfo=pytz.utc)
    if len(argv) == 5:
        utc = utc.replace(
            year=int(argv[1]), month=int(argv[2]), day=int(argv[3]), hour=int(argv[4])
        )
    run(utc)


if __name__ == "__main__":
    main(sys.argv)
