"""Create a Psuedo N0R composite based on N0Q.

The NWS no longer disseminates N0R, but we have lots of users of it and it
is generally a useful product for long term archives.
"""

# stdlib
import os
import sys
import time

# Third Party
import numpy as np
from PIL import Image, PngImagePlugin
from pyiem.util import logger, utc

LOG = logger()


def main(argv):
    """Go Main Go."""
    timestamp = argv[1]  # YYYYmmddHHMI
    outfn = argv[2]
    n0qfn = f"data/n0q_{timestamp}.png"
    attempt = 0
    while not os.path.isfile(n0qfn) and attempt < 10:
        LOG.info("File %s missing, sleeping 10 seconds", n0qfn)
        time.sleep(10)
        attempt += 1
    if not os.path.isfile(n0qfn):
        LOG.warning("Failed to find %s, aborting...", n0qfn)
        sys.exit(1)
    LOG.info("Processing %s", n0qfn)
    # Read in N0Q color index
    png = Image.open(n0qfn)
    sz = (png.size[1], png.size[0])
    cidx_grid = np.array(
        np.frombuffer(png.tobytes(), dtype=np.uint8).reshape(sz)
    )
    # Downscale to 0.01 res by simple striding, trim off 200 pixels
    cidx_grid = cidx_grid[:-200:2, :-200:2]
    # Convert N0Q to dbZ, careful of zero handling here
    dbz = np.where(cidx_grid > 0, cidx_grid * 0.5 - 32.5, -999)
    # Create new color index grid, 0th gets lost in this, oh well
    # NOTE: the -25 start of the range would appear to be an off-by-one
    # somewhere, but yields the best result.  Sloppy.
    cidx_grid = np.digitize(dbz, np.arange(-25, 75, 5), right=False)
    # Apply old N0R color table
    png = Image.fromarray(cidx_grid.astype(np.uint8))
    png.putpalette(Image.open("reference/n0r.png").getpalette())
    meta = PngImagePlugin.PngInfo()
    meta.add_text("gentime", utc().strftime("%Y-%m-%dT%H:%M:%SZ"))
    # Write out PNG
    png.save(outfn)


if __name__ == "__main__":
    main(sys.argv)
