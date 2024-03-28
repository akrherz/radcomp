"""
tmpc in the netcdf file is stored with 0,0 in lower left
PIL will have imagery with 0,0 in upper left
"""

import datetime
import sys

import numpy as np
from PIL import Image, PngImagePlugin
from pyiem.util import ncopen


def main(argv):
    """Run Main"""
    hour = int(argv[1])
    job = argv[2]
    sector = argv[3]
    netprod = argv[4]

    # Load EET
    netpng = Image.open(f"{sector}_{netprod}_{job}.gif")
    sz = (netpng.size[1], netpng.size[0])
    net = np.array(np.frombuffer(netpng.tobytes(), dtype=np.uint8).reshape(sz))

    if sector == "US":
        # Load up our tmpc surface data
        with ncopen("data/ructemps.nc") as nc:
            tmpc = nc.variables["tmpc"][hour, :, :]
        tmpc = np.flipud(tmpc)

        # mask out the net based on temperature
        net = np.where(tmpc > 3.0, net, 15)
    else:
        # No Filtering... for now
        net[:, :] = 15.0

    # Load N0Q
    n0qpng = Image.open(f"{sector}_N0Q_{job}.gif")
    n0q = (np.frombuffer(n0qpng.tobytes(), dtype=np.uint8)).reshape(sz)

    # Clean n0q
    if netprod == "EET":
        # EET idx 2 is 1 kft, so 6 is 5kft
        n0q = np.where(net < 6, 0, n0q)
    else:
        n0q = np.where(net < 2, 0, n0q)

    # Make the image, please!
    png = Image.fromarray(n0q)
    # png.putpalette( make_colorramp() )
    png.putpalette(n0qpng.getpalette())
    meta = PngImagePlugin.PngInfo()
    # This is racy if we have another processing at the same time and are
    # in a sector, like GU, that often produces blank images.
    meta.add_text(
        "gentime", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    png.save(f"{sector}_N0Q_CLEAN_{job}.png", pnginfo=meta)


if __name__ == "__main__":
    main(sys.argv)
