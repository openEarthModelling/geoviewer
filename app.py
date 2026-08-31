import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import panel as pn

from services.catalog import Catalog
from ui.file_browser import FileBrowser
from ui.variable_panel import VariablePanel
from ui.layout import build_layout

pn.extension()

roots = [p for p in os.environ.get("NC_VIEWER_ROOTS", "/data/GEOSChem").split(":") if p]
catalog = Catalog(roots)
fb = FileBrowser(catalog)
vp = VariablePanel()

# 选文件后枚举变量
def on_file(event):
    if event.new is None:
        return
    full = catalog.resolve(event.new)
    from readers import identify, get_reader
    reader = get_reader(identify(full))
    vp.set_variables(reader.list_variables(full))

fb.file_select.param.watch(on_file, "value")

layout = build_layout({
    "file_browser": fb,
    "variable_panel": vp,
    "map_panel": pn.pane.Markdown("（选择变量后显示地图）"),
    "controls": pn.pane.Markdown("（绘图控制）"),
    "metadata": pn.pane.Markdown("（元数据）"),
})
layout.servable()
