#!/usr/bin/env python
"""Use GDAL to do some cleaning"""
from __future__ import print_function
import os
import sys
import datetime

import numpy
import pytz
from PIL import Image, PngImagePlugin
from osgeo import gdal


def main(argv):
    """Our main method"""
    pid = argv[1]
    ts = datetime.datetime.strptime(argv[2], "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=pytz.utc)

    # Open base reflectivity layer (n0r)
    n0r = gdal.Open("n0r_%s_in.tif" % (pid,), 0)
    n0rd = n0r.ReadAsArray()

    for i in range(24):
        ts = ts - datetime.timedelta(hours=i)
        fn = "data/ifreeze-%s.tif" % (ts.strftime("%Y%m%d%H"),)
        if os.path.isfile(fn):
            break
    ifreeze = gdal.Open(fn, 0)
    ifr = ifreeze.ReadAsArray()

    # Open net echo tops composite
    net = gdal.Open("net_%s_in.tif" % (pid,), 0)
    # Winter mask for now
    v = net.ReadAsArray()
    # v[:,0:2400] = 10.
    # v[:1300,2400:] = 10.

    v = numpy.where(ifr > 0, 10.0, v)

    # Do the comparison of n0r vs net
    n0rd2 = numpy.where(v < 2.0, 0, n0rd)

    # Create output file
    png = Image.fromarray(n0rd2)
    n0rpng = Image.open("n0r_%s.gif" % (pid,))
    png.putpalette(n0rpng.getpalette())
    meta = PngImagePlugin.PngInfo()
    meta.add_text("gentime", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    png.save("test_%s.png" % (pid,), pnginfo=meta)


if __name__ == "__main__":
    main(sys.argv)
