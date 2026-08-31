import panel as pn

from readers.base import VarInfo
from services.dimension import auto_assign


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
            # 默认选中第一个能画出经纬度地图的变量（dims 能被 auto_assign 识别出 x/y），
            # 避免选到 lat/lon 坐标或 time_bnds 等非地图数据变量
            def is_mapable(i: VarInfo) -> bool:
                if not i.is_plottable:
                    return False
                role = auto_assign(list(i.dims))
                return role.x is not None and role.y is not None

            first_map = next((i for i in infos if is_mapable(i)), infos[0])
            self.var_select.value = first_map.path

    def get_info(self, path: str) -> VarInfo | None:
        return self._infos.get(path)
