"""GeoViews rendering pipeline: CRS-aware dataset building, feature overlays, rasterized maps."""
import geoviews as gv
import geoviews.feature as gf
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
