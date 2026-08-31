import panel as pn

from ui.layout import build_layout


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
