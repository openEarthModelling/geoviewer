import holoviews as hv
import numpy as np
import pytest
import xarray as xr
from cartopy import crs as ccrs

import ui.geo as geo
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


def _fake_features(monkeypatch):
    # Plain curves stand in for cartopy features: no download, fast, label-preserving
    monkeypatch.setattr(geo, "FEATURES", {
        name: hv.Curve([0, 1], label=name) for name in ("coastline", "borders", "grid")
    })


def test_feature_overlay_combines_enabled(monkeypatch):
    _fake_features(monkeypatch)
    overlay, unavailable = geo.feature_overlay(
        {"coastline": True, "borders": False, "grid": True})
    assert unavailable == []
    assert len(overlay) == 2


def test_feature_overlay_reports_unavailable(monkeypatch):
    _fake_features(monkeypatch)

    def broken_resolve(feature):
        if feature.label == "borders":
            raise OSError("offline")
        return feature

    monkeypatch.setattr(geo, "_resolve", broken_resolve)
    overlay, unavailable = geo.feature_overlay(
        {"coastline": True, "borders": True, "grid": True})
    assert unavailable == ["borders"]
    assert len(overlay) == 2


def test_feature_overlay_all_off_returns_none(monkeypatch):
    _fake_features(monkeypatch)
    overlay, unavailable = geo.feature_overlay(
        {"coastline": False, "borders": False, "grid": False})
    assert overlay is None
    assert unavailable == []


def test_feature_overlay_ignores_unknown_names(monkeypatch):
    _fake_features(monkeypatch)
    overlay, unavailable = geo.feature_overlay({"lakes": True})
    assert overlay is None
    assert unavailable == []
