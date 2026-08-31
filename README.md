# geoviewer

A browser-based viewer for geospatial scientific data — netCDF, HDF5, and GRIB — inspired by NASA Panoply.

Browse a whitelisted server directory, pick a variable, and get an interactive lat/lon map with a time/level slider, colormap control, and a metadata panel. It runs as a single [Panel](https://panel.holoviz.org) app served over the web, with no uploads — files stay on the server.

## Features

- **Multi-format readers** behind one interface: netCDF (classic and netCDF-4/HDF5-backed), HDF5, and GRIB (via cfgrib/eccodes).
- **Variable list** with automatic dimension-role detection (`x`/`y`/`z`/`time`) via naming heuristics and unit hints.
- **Interactive map** rendered with datashader rasterization (falls back to plain rendering when unavailable).
- **Time and vertical-level sliders** for N-D variables.
- **Colormap picker** and per-dimension role overrides.
- **Metadata panel** showing the selected variable's attributes.
- **Directory whitelist** with path-traversal protection — server-side browsing only.

## Installation

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

GRIB support needs the eccodes C library; the `eccodes` wheel bundles it, or install it system-wide (`conda install -c conda-forge eccodes`).

## Usage

Start the server, pointing `NC_VIEWER_ROOTS` at one or more directories to browse (colon-separated):

```bash
NC_VIEWER_ROOTS=/data/mydata:/data/more python -m panel serve app.py --port 5006
```

Then open http://localhost:5006/app.

To serve on a remote machine, use an SSH tunnel:

```bash
ssh -L 5006:127.0.0.1:5006 user@host
```

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NC_VIEWER_ROOTS` | `.` | Colon-separated whitelisted directories to browse |
| `NUMBA_CACHE_DIR` | `<tmp>/numba_cache` | Numba JIT cache directory (used by datashader rasterization) |

## Architecture

```
readers/   unified Reader abstraction (netCDF / HDF5 / GRIB) -> xarray
services/  catalog whitelist, dimension role model, slice LRU cache
ui/        Panel components (file browser, variable panel, map, controls, metadata)
app.py     Panel entrypoint wiring callbacks
```

## Testing

```bash
python -m pytest -q
```

## License

[Apache-2.0](LICENSE)
