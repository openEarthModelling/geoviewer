import panel as pn

from services.dimension import RoleAssignment, auto_assign

_ROLES = ["x", "y", "z", "time", "fixed"]


class Controls(pn.Column):
    """Control panel: mode toggle, time slider, colormap, per-dimension role selectors."""

    def __init__(self):
        self.mode_toggle = pn.widgets.RadioButtonGroup(
            label="模式", options=["自动", "手动"], value="自动"
        )
        # end=1 avoids the start==end Bokeh E-1021 warning; sliders are inert until a variable is selected
        self.time_slider = pn.widgets.IntSlider(label="时间步", start=0, end=1, value=0)
        self.level_slider = pn.widgets.IntSlider(label="层", start=0, end=1, value=0)
        self.cmap_select = pn.widgets.Select(
            label="调色板",
            options=["turbo", "viridis", "cividis", "magma", "inferno", "RdBu_r"],
            value="turbo",
        )
        self.role_widgets = {}
        super().__init__(self.mode_toggle, self.time_slider, self.level_slider,
                         self.cmap_select)

    def set_dims(self, dims: list[str], role: RoleAssignment = None):
        """Build a role selector per dimension; infer via auto_assign when role is absent."""
        if role is None:
            role = auto_assign(dims)
        # Remove old role widgets to avoid accumulation
        for w in list(self.role_widgets.values()):
            try:
                self.remove(w)
            except Exception:
                pass
        self.role_widgets = {}
        self.time_slider.start = 0
        self.time_slider.end = 1
        self.time_slider.value = 0
        self.level_slider.start = 0
        self.level_slider.end = 1
        self.level_slider.value = 0
        for d in dims:
            # Role label ("x"/"y"/"z"/"time"/"fixed"), not the dimension name
            label = ("x" if d == role.x else
                     "y" if d == role.y else
                     "z" if d == role.z else
                     "time" if d == role.time else "fixed")
            w = pn.widgets.Select(
                label=f"维度 {d}",
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
