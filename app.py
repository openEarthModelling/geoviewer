import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# datashader relies on numba's jit cache; some environments raise "no locator
# available" with the default cache location, so redirect to a writable /tmp
# dir (must be set before importing panel/hvplot).
os.environ.setdefault("NUMBA_CACHE_DIR", os.path.join(tempfile.gettempdir(), "numba_cache"))

import panel as pn

from readers import identify, get_reader
from services.catalog import Catalog
from services.dimension import auto_assign
from services.slice import SliceService
from ui.controls import Controls
from ui.file_browser import FileBrowser
from ui.layout import build_layout
from ui.map_panel import MapPanel
from ui.metadata_panel import MetadataPanel
from ui.variable_panel import VariablePanel

pn.extension()

roots = [p for p in os.environ.get("NC_VIEWER_ROOTS", ".").split(":") if p]
catalog = Catalog(roots)
slice_svc = SliceService()
fb = FileBrowser(catalog)
vp = VariablePanel()
mp = MapPanel()
ctl = Controls()
mdp = MetadataPanel()
status_bar = pn.pane.Markdown("格式：— · dims：— · 加载：就绪")

state = {"file": None, "var": None, "fmt": None, "dims": [], "sizes": {}, "auto_role": None}


def render():
    if state["file"] is None or state["var"] is None:
        return
    if ctl.mode_toggle.value == "手动":
        role = ctl.build_role()
    else:
        role = state["auto_role"]
    if role is None:
        return
    # Take the current time/level slice; fixed dims are sliced at index 0
    slices = {}
    if role.time and role.time in state["dims"]:
        slices[role.time] = ctl.time_slider.value
    if role.z and role.z in state["dims"]:
        slices[role.z] = ctl.level_slider.value
    for d, idx in role.fixed.items():
        slices[d] = idx
    da = slice_svc.get(state["file"], state["var"], slices)
    if role.x and role.y:
        mp.set_data(state["file"], state["var"], da, x=role.x, y=role.y,
                    cmap=ctl.cmap_select.value)
    else:
        mp.show_message("该变量无经纬度坐标，无法绘制地图")


def _watch_role_widgets():
    # Role selectors are created dynamically in set_dims, so re-attach listeners after each rebuild
    for w in ctl.role_widgets.values():
        w.param.watch(lambda e: render(), "value")


def on_file(event):
    if event.new is None:
        return
    full = catalog.resolve(event.new)
    fmt = identify(full)
    reader = get_reader(fmt)
    infos = reader.list_variables(full)
    # Set file state and clear the old variable/panels first, then fill the
    # variable list: set_variables assigns var_select.value synchronously and
    # triggers on_var, which must read the new file.
    state["file"] = full
    state["fmt"] = fmt
    state["var"] = None
    state["auto_role"] = None
    mp.clear()
    mdp.clear()
    vp.set_variables(infos)
    status_bar.object = f"格式：{fmt} · 文件：{event.new} · 加载：就绪"


def on_var(event):
    if event.new is None:
        return
    if state["file"] is None:
        return
    state["var"] = event.new
    info = vp.get_info(event.new)
    if info is None:
        return
    # Use VarInfo's dims/shape for dimension detection without reading the whole variable
    state["dims"] = list(info.dims)
    state["sizes"] = dict(zip(info.dims, info.shape))
    role = auto_assign(state["dims"])
    state["auto_role"] = role
    ctl.set_dims(state["dims"], role)
    _watch_role_widgets()
    if role.time and role.time in state["sizes"]:
        ctl.time_slider.end = state["sizes"][role.time] - 1
    if role.z and role.z in state["sizes"]:
        ctl.level_slider.end = state["sizes"][role.z] - 1
    mdp.show(state["file"], state["var"])
    status_bar.object = f"格式：{state['fmt']} · dims：{info.shape} · 加载：就绪"
    render()


def safe(fn):
    def wrapper(*a, **k):
        try:
            fn(*a, **k)
        except Exception as e:
            pn.state.notifications.error(str(e))
    return wrapper


render = safe(render)
on_file = safe(on_file)
on_var = safe(on_var)

fb.file_select.param.watch(on_file, "value")
vp.var_select.param.watch(on_var, "value")
ctl.time_slider.param.watch(lambda e: render(), "value")
ctl.level_slider.param.watch(lambda e: render(), "value")
ctl.cmap_select.param.watch(lambda e: render(), "value")
ctl.mode_toggle.param.watch(lambda e: render(), "value")

layout = build_layout({
    "file_browser": fb,
    "variable_panel": vp,
    "map_panel": mp,
    "controls": ctl,
    "metadata": mdp,
})
layout.append(status_bar)
layout.servable()
