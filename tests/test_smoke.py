import numpy as np
import panel as pn
import xarray as xr

from services.catalog import Catalog
from ui.controls import Controls
from ui.file_browser import FileBrowser
from ui.map_panel import MapPanel
from ui.variable_panel import VariablePanel
from ui.layout import build_layout
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
