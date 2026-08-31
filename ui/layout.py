import panel as pn


def build_layout(panels: dict) -> pn.Column:
    """三栏固定布局。panels 键：file_browser/variable_panel/map_panel/controls/metadata。"""
    left = pn.Column(
        pn.pane.Markdown("### 文件与变量"),
        panels["file_browser"],
        panels["variable_panel"],
        width=300,
        sizing_mode="stretch_height",
    )
    right = pn.Column(
        panels["controls"],
        panels["metadata"],
        width=340,
        sizing_mode="stretch_height",
    )
    center = pn.Column(
        panels["map_panel"],
        sizing_mode="stretch_both",
    )
    main = pn.Row(left, center, right, sizing_mode="stretch_both")
    return pn.Column(
        pn.pane.Markdown("# Web NC 数据查看器"),
        main,
        sizing_mode="stretch_both",
    )
