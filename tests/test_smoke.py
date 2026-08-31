import netCDF4
import os
import numpy as np
import panel as pn
import pytest
import xarray as xr

from services.catalog import Catalog
from services.dimension import auto_assign
from ui.controls import Controls
from ui.file_browser import FileBrowser
from ui.map_panel import MapPanel
from ui.variable_panel import VariablePanel
from ui.layout import build_layout
from ui.metadata_panel import MetadataPanel
from readers import identify, get_reader
from readers.base import VarInfo


def test_build_layout_returns_panel():
    panels = {
        "file_browser": pn.pane.Markdown("files"),
        "variable_panel": pn.pane.Markdown("vars"),
        "map_panel": pn.pane.Markdown("map"),
        "controls": pn.pane.Markdown("ctrl"),
        "metadata": pn.pane.Markdown("meta"),
    }
    layout = build_layout(panels)
    assert isinstance(layout, pn.Column)


def test_file_browser_select(tmp_path):
    (tmp_path / "a.nc").write_bytes(b"x")
    fb = FileBrowser(Catalog([str(tmp_path)]))
    assert fb.file_select.value is None
    fb.file_select.value = str(tmp_path / "a.nc")


def test_variable_panel_set():
    vp = VariablePanel()
    vp.set_variables([VarInfo(path="v", name="v", shape=(2, 2),
                              dims=("x", "y"), is_plottable=True, format="netcdf")])
    assert vp.var_select.value == "v"


def test_variable_panel_defaults_to_mapable():
    """Defaults to the first plottable variable whose dims auto_assign recognizes as lat/lon (x/y).

    Regression: the lat coordinate and time_bnds (time,nbnd, not lat/lon) must
    not be selected by default; TREFHT should be.
    """
    infos = [
        VarInfo(path="lat", name="lat", shape=(5,), dims=("lat",), is_plottable=False, format="netcdf"),
        VarInfo(path="time_bnds", name="time_bnds", shape=(3, 2), dims=("time", "nbnd"), is_plottable=True, format="netcdf"),
        VarInfo(path="TREFHT", name="TREFHT", shape=(3, 5, 6), dims=("time", "lat", "lon"), is_plottable=True, format="netcdf"),
    ]
    vp = VariablePanel()
    vp.set_variables(infos)
    assert vp.var_select.value == "TREFHT"


def test_map_panel_render():
    mp = MapPanel()
    da = xr.DataArray(np.zeros((4, 5)), dims=("lat", "lon"))
    mp.set_data("/tmp/a.nc", "v", da, x="lon", y="lat")
    assert mp.pane is not None


def test_controls_time_slider():
    c = Controls()
    c.set_dims(["time", "lat", "lon"])
    assert c.time_slider.value == 0
    c.time_slider.value = 2
    assert c.time_slider.value == 2


def test_metadata_panel(tmp_path):
    p = tmp_path / "m.nc"
    ds = netCDF4.Dataset(p, "w")
    ds.createDimension("x", 2)
    v = ds.createVariable("v", "f8", ("x",))
    v.units = "K"
    ds.close()
    mp = MetadataPanel()
    mp.show(str(p), "v")
    assert "units" in str(mp.pane.object)


def test_end_to_end_nc(tmp_path):
    """Full pipeline: identify -> list -> read_slice -> auto_assign."""
    p = tmp_path / "e2e.nc"
    ds = netCDF4.Dataset(p, "w")
    for d in ("time", "lat", "lon"):
        ds.createDimension(d, 3)
    v = ds.createVariable("t", "f8", ("time", "lat", "lon"))
    v[:] = np.arange(27).reshape(3, 3, 3)
    ds.close()
    reader = get_reader(identify(str(p)))
    infos = reader.list_variables(str(p))
    assert infos[0].path == "t"
    da = reader.read_slice(str(p), "t", {"time": 1})
    role = auto_assign(list(da.dims))
    assert role.x == "lon"
    assert role.y == "lat"


def test_app_integration_4d(tmp_path):
    """Drive the app.py callbacks: open a 4-D netCDF -> variable detection -> map render."""
    try:
        import app
    except ImportError:
        pytest.skip("app cannot be imported in this environment")

    # 4-D variable (time, lev, lat, lon)
    p = tmp_path / "app_it.nc"
    ds = netCDF4.Dataset(p, "w")
    for d, n in (("time", 2), ("lev", 3), ("lat", 4), ("lon", 5)):
        ds.createDimension(d, n)
    v = ds.createVariable("v", "f8", ("time", "lev", "lat", "lon"))
    v[:] = np.arange(2 * 3 * 4 * 5).reshape(2, 3, 4, 5)
    ds.close()

    # Add the temp dir to the whitelist so catalog.resolve can hit it
    app.catalog.roots.append(os.path.realpath(str(tmp_path)))
    app.fb.file_select.value = str(p)

    assert app.vp.var_select.options
    assert app.vp.var_select.value == "v"
    app.vp.var_select.value = "v"

    assert app.state["auto_role"].x == "lon"
    assert app.mp.pane.object is not None
