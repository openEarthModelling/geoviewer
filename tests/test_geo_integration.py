"""Integration tests with real Natural Earth feature data (download-gated).

They clear proxy variables first: the dev box's clash proxy breaks the
Natural Earth download (connection reset), direct connections work. If the
data is unreachable the tests SKIP (not fail) so offline CI stays green.
"""
import holoviews as hv
import numpy as np
import pytest
import xarray as xr

from ui.geo import render_geo_map

hv.extension("bokeh")

ALL_ON = {"coastline": True, "borders": True, "grid": True}


@pytest.fixture(autouse=True)
def no_proxy(monkeypatch):
    for var in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
                "all_proxy", "ALL_PROXY"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def da():
    lat = np.linspace(-60, 60, 30)
    lon = np.linspace(0, 350, 40)
    return xr.DataArray(np.random.rand(30, 40), coords={"lat": lat, "lon": lon},
                        dims=("lat", "lon"), name="T2M")


def test_full_pipeline_with_real_features(da):
    plot, unavailable = render_geo_map(da, "lon", "lat", features=ALL_ON)
    if unavailable:
        pytest.skip(f"Natural Earth data unreachable: {unavailable}")
    assert hv.renderer("bokeh").get_plot(plot) is not None
