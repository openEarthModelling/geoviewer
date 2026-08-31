import hvplot.xarray
import panel as pn


class MapPanel(pn.Column):
    """地图面板：用 hvplot 渲染 2D 数据切片。"""

    def __init__(self):
        self.pane = pn.pane.HoloViews(sizing_mode="stretch_both")
        super().__init__(self.pane)

    def set_data(self, path, var_path, da, x, y, cmap="turbo", clim=None):
        # 无名 DataArray 会让 holoviews 缺 value 维度，先补名
        if getattr(da, "name", None) is None:
            da = da.rename(var_path or "value")
        try:
            plot = da.hvplot(
                x=x, y=y,
                cmap=cmap,
                rasterize=True,
                width=700, height=500,
            )
        except Exception:
            # datashader/numba 不可用（如 numpy 2.4 与 numba 不兼容）时退化为普通渲染
            plot = da.hvplot(
                x=x, y=y,
                cmap=cmap,
                rasterize=False,
                width=700, height=500,
            )
        if clim is not None:
            plot = plot.opts(clim=clim)
        self.pane.object = plot

    def clear(self):
        self.pane.object = None
