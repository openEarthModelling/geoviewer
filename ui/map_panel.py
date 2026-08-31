import hvplot.xarray  # noqa: F401 -- registers the xarray accessor used by `da.hvplot`
import panel as pn


class MapPanel(pn.Column):
    """Map panel: renders 2D data slices with hvplot."""

    def __init__(self):
        self.pane = pn.pane.HoloViews(sizing_mode="stretch_both")
        self.message = pn.pane.Markdown("")
        super().__init__(self.pane, self.message)

    def set_data(self, path, var_path, da, x, y, cmap="turbo", clim=None):
        # An unnamed DataArray makes holoviews miss the value dimension, so name it first
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
            # Fall back to plain rendering when datashader/numba is unavailable (e.g. numpy 2.4 vs numba incompatibility)
            plot = da.hvplot(
                x=x, y=y,
                cmap=cmap,
                rasterize=False,
                width=700, height=500,
            )
        if clim is not None:
            plot = plot.opts(clim=clim)
        self.message.object = ""
        self.pane.object = plot

    def clear(self):
        self.pane.object = None
        self.message.object = ""

    def show_message(self, text: str):
        """Show a Markdown message when no lat/lon coordinates exist, instead of silently clearing."""
        self.pane.object = None
        self.message.object = text
