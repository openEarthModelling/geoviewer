import panel as pn

from readers import get_reader, identify


class MetadataPanel(pn.Column):
    """Metadata panel: shows the current variable's attributes."""

    def __init__(self):
        self.pane = pn.pane.Markdown("（未选择变量）")
        super().__init__(pn.pane.Markdown("### 元数据"), self.pane)

    def show(self, path: str, var_path: str):
        reader = get_reader(identify(path))
        attrs = reader.read_metadata(path, var_path)
        lines = [f"**{k}** = `{v}`" for k, v in attrs.items()]
        self.pane.object = "\n".join(lines) if lines else "（无属性）"

    def clear(self):
        self.pane.object = "（未选择变量）"
