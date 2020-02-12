"""
  tmpc in the netcdf file is stored with 0,0 in lower left
  PIL will have imagery with 0,0 in upper left
"""
import sys
import datetime

from PIL import Image
from PIL import PngImagePlugin
import numpy as np
from pyiem.util import ncopen


def main(argv):
    """Run Main"""
    hour = int(argv[1])
    job = argv[2]
    sector = argv[3]
    netprod = argv[4]

    # Load EET
    netpng = Image.open("%s_%s_%s.gif" % (sector, netprod, job))
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
    n0qpng = Image.open("%s_N0Q_%s.gif" % (sector, job))
    n0q = (np.frombuffer(n0qpng.tobytes(), dtype=np.uint8)).reshape(sz)

    # Clean n0q
    if netprod == "EET":
        n0q = np.where(net < 10, 0, n0q)
    else:
        n0q = np.where(net < 2, 0, n0q)

    # Make the image, please!
    png = Image.fromarray(n0q)
    # png.putpalette( make_colorramp() )
    png.putpalette(n0qpng.getpalette())
    meta = PngImagePlugin.PngInfo()
    meta.add_text("gentime", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    png.save("%s_N0Q_CLEAN_%s.png" % (sector, job), pnginfo=meta)


if __name__ == "__main__":
    main(sys.argv)
