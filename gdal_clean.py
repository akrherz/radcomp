#!/usr/bin/env python
"""Use GDAL to do some cleaning"""

import datetime
import os
import sys
from zoneinfo import ZoneInfo

import numpy
from osgeo import gdal
from PIL import Image, PngImagePlugin

gdal.UseExceptions()


def main(argv):
    """Our main method"""
    pid = argv[1]
    ts = datetime.datetime.strptime(argv[2], "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=ZoneInfo("UTC"))

    # Open base reflectivity layer (n0r)
    n0r = gdal.Open(f"n0r_{pid}_in.tif", 0)
    n0rd = n0r.ReadAsArray()

    for _i in range(24):
        fn = f"data/ifreeze-{ts:%Y%m%d%H}.tif"
        if os.path.isfile(fn):
            break
        ts -= datetime.timedelta(hours=1)
    ifreeze = gdal.Open(fn, 0)
    ifr = ifreeze.ReadAsArray()

    # Open net echo tops composite
    net = gdal.Open(f"net_{pid}_in.tif", 0)
    # Winter mask for now
    v = net.ReadAsArray()
    # This product needs downscaled and trimmed
    v = v[:-200:2, :-200:2]
    # v[:,0:2400] = 10.
    # v[:1300,2400:] = 10.

    v = numpy.where(ifr > 0, 10.0, v)

    # Do the comparison of n0r vs net (EET)
    # EET color index 2 is 1 kft, so 6 is 5kft
    n0rd2 = numpy.where(v < 6.0, 0, n0rd)

    # Create output file
    png = Image.fromarray(n0rd2)
    n0rpng = Image.open(f"n0r_{pid}.png")
    png.putpalette(n0rpng.getpalette())
    meta = PngImagePlugin.PngInfo()
    meta.add_text(
        "gentime", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    png.save(f"test_{pid}.png", pnginfo=meta)


if __name__ == "__main__":
    main(sys.argv)
