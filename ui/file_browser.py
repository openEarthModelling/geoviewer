import os

import panel as pn

from services.catalog import Catalog, PathOutsideWhitelist


class FileBrowser(pn.Column):
    """File browser: a path input plus subdirectory/file selects, browsing only whitelisted roots.

    The path input shows the current absolute path and accepts an absolute or
    relative path (jump on Enter); the subdirectory select drills down; the file
    select lists openable files in the current directory.
    """

    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        self.path_input = pn.widgets.TextInput(
            label="路径", placeholder="绝对/相对路径，回车跳转"
        )
        self.dir_select = pn.widgets.Select(label="子目录", options={}, value=None)
        self.file_select = pn.widgets.Select(label="文件", options={}, value=None)
        self.msg = pn.pane.Markdown("", sizing_mode="stretch_width")
        super().__init__(self.path_input, self.dir_select, self.file_select, self.msg)

        self._cwd = ""       # current directory (relative to the whitelist root)
        self._guard = False  # suppress callbacks while back-filling path_input

        def on_path(event):
            if self._guard:
                return
            self._navigate(event.new or "")

        def on_dir(event):
            if event.new is None:
                return
            self._navigate(os.path.join(self._cwd, event.new))

        self.path_input.param.watch(on_path, "value")
        self.dir_select.param.watch(on_dir, "value")
        self._navigate("")

    def _navigate(self, raw: str):
        try:
            rel = self.catalog.to_rel(raw)
        except PathOutsideWhitelist:
            self.msg.object = "❌ 路径越界：只能访问白名单根目录内"
            return
        full = self.catalog.resolve(rel)
        if not os.path.isdir(full):
            self.msg.object = "❌ 目录不存在或不是目录"
            return
        self._cwd = rel
        self._guard = True
        try:
            self.path_input.value = full  # back-fill the absolute path
        finally:
            self._guard = False
        entries = self.catalog.list_dir(rel)
        dirs = {e.name: "📁 " + e.name for e in entries if e.is_dir}
        files = {e.path: e.name for e in entries if not e.is_dir}
        self.dir_select.options = dirs
        self.dir_select.value = None
        self.file_select.options = files
        self.file_select.value = None
        self.msg.object = f"当前目录：{full} · {len(files)} 个文件 · {len(dirs)} 个子目录"
