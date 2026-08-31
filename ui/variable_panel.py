import panel as pn

from readers.base import VarInfo


class VariablePanel(pn.Column):
    """变量面板：展示当前文件的可选变量。"""

    def __init__(self):
        self.var_select = pn.widgets.Select(name="变量", options=[], value=None)
        self._infos = {}
        super().__init__(self.var_select)

    def set_variables(self, infos: list[VarInfo]):
        self._infos = {i.path: i for i in infos}
        self.var_select.options = {i.path: i.name for i in infos}
        if infos:
            self.var_select.value = infos[0].path

    def get_info(self, path: str) -> VarInfo | None:
        return self._infos.get(path)
