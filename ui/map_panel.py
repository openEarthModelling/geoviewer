import panel as pn

from ui.geo import render_geo_map


class MapPanel(pn.Column):
    """Map panel: renders 2D data slices through the GeoViews pipeline."""

    def __init__(self):
        self.pane = pn.pane.HoloViews(sizing_mode="stretch_both")
        self.message = pn.pane.Markdown("")
        super().__init__(self.pane, self.message)

    def set_data(self, path, var_path, da, x, y, cmap="turbo", clim=None,
                 features=None):
        # An unnamed DataArray makes geoviews miss the value dimension, so name it first
        if getattr(da, "name", None) is None:
            da = da.rename(var_path or "value")
        plot, unavailable = render_geo_map(da, x, y, features=features or {},
                                           cmap=cmap, clim=clim)
        if unavailable:
            # The data layer rendered fine; only the overlays could not be loaded
            pn.state.notifications.warning(f"地理要素离线不可用:{', '.join(unavailable)}")
        self.message.object = ""
        self.pane.object = plot

    def clear(self):
        self.pane.object = None
        self.message.object = ""

    def show_message(self, text: str):
        """Show a Markdown message when no lat/lon coordinates exist, instead of silently clearing."""
        self.pane.object = None
        self.message.object = text
