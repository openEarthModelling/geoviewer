import panel as pn

from services.catalog import Catalog


class FileBrowser(pn.Column):
    """文件浏览器：目录选择 + 文件选择，仅浏览白名单根目录。"""

    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        self.file_select = pn.widgets.Select(name="文件", options=[], value=None)
        self._dir = pn.widgets.Select(name="目录", options=[""], value="")
        super().__init__(self._dir, self.file_select)

        def on_dir(event):
            self._refresh_files(event.new)

        self._dir.param.watch(on_dir, "value")
        self._refresh_files("")

    def _refresh_files(self, rel: str):
        entries = self.catalog.list_dir(rel)
        dirs = [("", "… (根目录)")] + [
            (e.path, "📁 " + e.name) for e in entries if e.is_dir
        ]
        files = [e for e in entries if not e.is_dir]
        self._dir.options = {p: label for p, label in dirs}
        self.file_select.options = {e.path: e.name for e in files}
