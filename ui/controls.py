import panel as pn

from services.dimension import RoleAssignment, auto_assign

_ROLES = ["x", "y", "z", "time", "fixed"]


class Controls(pn.Column):
    """控制面板：模式切换、时间滑块、调色板、每维度角色选择。"""

    def __init__(self):
        self.mode_toggle = pn.widgets.RadioButtonGroup(
            name="模式", options=["自动", "手动"], value="自动"
        )
        self.time_slider = pn.widgets.IntSlider(name="时间步", start=0, end=0, value=0)
        self.level_slider = pn.widgets.IntSlider(name="层", start=0, end=0, value=0)
        self.cmap_select = pn.widgets.Select(
            name="调色板",
            options=["turbo", "viridis", "cividis", "magma", "inferno", "RdBu_r"],
            value="turbo",
        )
        self.role_widgets = {}
        super().__init__(self.mode_toggle, self.time_slider, self.level_slider,
                         self.cmap_select)

    def set_dims(self, dims: list[str], role: RoleAssignment = None):
        """为每个维度建角色选择下拉框；role 缺省时用 auto_assign 推断。"""
        if role is None:
            role = auto_assign(dims)
        # 清空旧的 role widgets，避免重复累积
        for w in list(self.role_widgets.values()):
            try:
                self.remove(w)
            except Exception:
                pass
        self.role_widgets = {}
        self.time_slider.start = 0
        self.time_slider.end = 0
        self.time_slider.value = 0
        self.level_slider.start = 0
        self.level_slider.end = 0
        self.level_slider.value = 0
        for d in dims:
            # 角色标签（"x"/"y"/"z"/"time"/"fixed"），不是维度名
            label = ("x" if d == role.x else
                     "y" if d == role.y else
                     "z" if d == role.z else
                     "time" if d == role.time else "fixed")
            w = pn.widgets.Select(
                name=f"维度 {d}",
                options=_ROLES + ["忽略"],
                value=label,
            )
            self.role_widgets[d] = w
            self.append(w)

    def build_role(self) -> RoleAssignment:
        ra = RoleAssignment()
        for d, w in self.role_widgets.items():
            v = w.value
            if v == "x":
                ra.x = d
            elif v == "y":
                ra.y = d
            elif v == "z":
                ra.z = d
            elif v == "time":
                ra.time = d
            elif v == "fixed":
                ra.fixed[d] = 0
        return ra
