"""
Use the RAP model to provide a mask for use in clutter suppression by
the NEXRAD compositer
"""

import datetime
import os
import tempfile

import numpy as np
import pygrib
import pyproj
import requests
from affine import Affine
from osgeo import gdal, gdalconst
from pyiem.util import logger, utc
from rasterio.warp import Resampling, reproject

LOG = logger()
gdal.UseExceptions()


def get_grid(grb):
    """Figure out the x-y coordinates."""
    pj = pyproj.Proj(grb.projparams)
    # ll
    lat1 = grb["latitudeOfFirstGridPointInDegrees"]
    lon1 = grb["longitudeOfFirstGridPointInDegrees"]
    llx, lly = pj(lon1, lat1)
    xaxis = llx + grb["DxInMetres"] * np.arange(grb["Nx"])
    yaxis = lly + grb["DyInMetres"] * np.arange(grb["Ny"])
    return xaxis, yaxis


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
                src_crs = grbs[0].projparams
                xaxis, yaxis = get_grid(grbs[0])
                src_aff = Affine(
                    grbs[0]["DxInMetres"],
                    0.0,
                    xaxis[0],
                    0.0,
                    -grbs[0]["DyInMetres"],
                    yaxis[-1],
                )
                tmpk_2m = grbs[0].values
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

    tmpk = np.zeros((2600, 6000), "f")
    dest_aff = Affine(0.01, 0.0, -126.0, 0.0, -0.01, 50.0)
    reproject(
        np.flipud(tmpk_2m),
        tmpk,
        src_transform=src_aff,
        src_crs=src_crs,
        dst_transform=dest_aff,
        dst_crs={"init": "EPSG:4326"},
        dst_nodata=np.nan,
        resampling=Resampling.nearest,
    )

    # Anything less than 6 C we will not consider for masking
    ifreezing = np.ma.where(tmpk < 279.0, 1.0, 0.0)
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
