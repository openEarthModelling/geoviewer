import panel as pn

from readers.base import VarInfo
from services.dimension import auto_assign


class VariablePanel(pn.Column):
    """Variable panel: shows the selectable variables of the current file."""

    def __init__(self):
        self.var_select = pn.widgets.Select(label="变量", options=[], value=None)
        self._infos = {}
        super().__init__(self.var_select)

    def set_variables(self, infos: list[VarInfo]):
        self._infos = {i.path: i for i in infos}
        self.var_select.options = {i.path: i.name for i in infos}
        if infos:
            # Default to the first variable that can produce a lat/lon map (dims
            # are recognized as x/y by auto_assign), avoiding coordinate
            # variables like lat/lon or time_bnds.
            def is_mapable(i: VarInfo) -> bool:
                if not i.is_plottable:
                    return False
                role = auto_assign(list(i.dims))
                return role.x is not None and role.y is not None

            first_map = next((i for i in infos if is_mapable(i)), infos[0])
            self.var_select.value = first_map.path

    def get_info(self, path: str) -> VarInfo | None:
        return self._infos.get(path)
