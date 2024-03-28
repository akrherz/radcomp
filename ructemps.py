"""Merge Grib2 RAP temps into netcdf file."""

import datetime
import os
import sys
import tempfile

import numpy as np
import pygrib
import pyproj
import requests
from affine import Affine
from metpy.units import units
from pyiem.util import logger, ncopen, utc
from rasterio.warp import Resampling, reproject

LOG = logger()


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
                LOG.info(exp)
                continue
            if grbs:
                break
    os.unlink(tmpfd.name)

    if tmpk_2m is None:
        LOG.warning("No data found for %s", utcnow)
        return

    with ncopen("data/ructemps.nc", "a") as nc:
        tmpk = np.zeros(
            (nc.dimensions["lat"].size, nc.dimensions["lon"].size), "f"
        )
        top = nc.variables["lat"][-1]
        dy = nc.variables["lat"][1] - nc.variables["lat"][0]
        left = nc.variables["lon"][0]
        dx = nc.variables["lon"][1] - nc.variables["lon"][0]
        dest_aff = Affine(dx, 0.0, left, 0.0, -dy, top)
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
        data = nc.variables["tmpc"]
        writehr = utcnow.hour
        # Our netcdf storage is simple int8, so -256 to 255
        # our usage is crude, so we set any missing values to 200 as they
        # won't matter anyway
        val = (units("degK") * np.flipud(tmpk)).to(units("degC")).m
        val = np.where(np.isnan(val), 200, val)
        data[writehr, :, :] = val


if __name__ == "__main__":
    main(sys.argv)
