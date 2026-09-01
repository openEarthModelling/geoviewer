import holoviews as hv
import numpy as np
import pytest
import xarray as xr
from cartopy import crs as ccrs

from ui.geo import build_element

hv.extension("bokeh")


@pytest.fixture
def da():
    lat = np.linspace(-60, 60, 10)
    lon = np.linspace(0, 350, 12)
    return xr.DataArray(np.random.rand(10, 12), coords={"lat": lat, "lon": lon},
                        dims=("lat", "lon"), name="T2M")


def test_build_element_dims(da):
    ds = build_element(da, "lon", "lat")
    assert [d.name for d in ds.kdims] == ["lon", "lat"]
    assert [d.name for d in ds.vdims] == ["T2M"]


def test_build_element_default_crs_is_plate_carree(da):
    assert build_element(da, "lon", "lat").crs == ccrs.PlateCarree()


def test_build_element_explicit_crs(da):
    assert build_element(da, "lon", "lat", crs=ccrs.Robinson()).crs == ccrs.Robinson()


def test_build_element_unnamed_da_gets_value_name():
    # geoviews loses the value dimension on unnamed DataArrays
    da = xr.DataArray(np.zeros((4, 5)), dims=("lat", "lon"))
    assert [d.name for d in build_element(da, "lon", "lat").vdims] == ["value"]


def test_build_element_missing_coords_get_default_range():
    # Synthetic arrays without coordinates must still render (test_smoke relies on this)
    da = xr.DataArray(np.zeros((4, 5)), dims=("lat", "lon"), name="v")
    ds = build_element(da, "lon", "lat")
    assert [d.name for d in ds.kdims] == ["lon", "lat"]
