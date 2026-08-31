import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import panel as pn

from ui.layout import build_layout

pn.extension()

placeholder = pn.pane.Markdown("（占位）")
layout = build_layout({
    "file_browser": placeholder,
    "variable_panel": placeholder,
    "map_panel": placeholder,
    "controls": placeholder,
    "metadata": placeholder,
})
layout.servable()
