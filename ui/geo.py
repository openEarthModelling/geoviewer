"""GeoViews rendering pipeline: CRS-aware dataset building, feature overlays, rasterized maps."""
import geoviews as gv
import geoviews.feature as gf
import holoviews as hv
import numpy as np
from cartopy import crs as ccrs

# Feature registry: name -> GeoViews feature element. Add lakes/rivers/states here later.
FEATURES = {"coastline": gf.coastline, "borders": gf.borders, "grid": gf.grid}


def build_element(da, x, y, *, crs=None):
    """DataArray -> gv.Dataset with a CRS attached.

    Callers pick their own view: gv.Image for the rasterize path, gv.QuadMesh
    for the direct-render fallback. An unnamed DataArray is renamed to "value"
    (geoviews loses the value dimension otherwise); missing x/y coordinates
    get a default integer range so synthetic arrays still render.
    """
    if getattr(da, "name", None) is None:
        da = da.rename("value")
    if x not in da.coords:
        da = da.assign_coords({x: np.arange(da.sizes[x])})
    if y not in da.coords:
        da = da.assign_coords({y: np.arange(da.sizes[y])})
    return gv.Dataset(da, kdims=[x, y], vdims=[da.name], crs=crs or ccrs.PlateCarree())


def _resolve(feature):
    """Force feature geometry load now instead of at pane render time.

    Rendering the feature headlessly triggers the Natural Earth download here,
    where a failure is catchable -- the map pane must never die because a
    coastline download failed (spike-verified: offline raises URLError here).
    """
    hv.renderer("bokeh").get_plot(feature)
    return feature


def feature_overlay(features):
    """{name: enabled} -> (overlay element | None, unavailable names).

    Enabled features are force-loaded via _resolve; load failures are skipped
    and reported so callers can warn while still showing the data layer.
    All-off or all-failed gives (None, names).
    """
    overlay, unavailable = None, []
    for name, enabled in features.items():
        if not enabled or name not in FEATURES:
            continue
        try:
            element = _resolve(FEATURES[name])
        except Exception:
            unavailable.append(name)
            continue
        overlay = element if overlay is None else overlay * element
    return overlay, unavailable
