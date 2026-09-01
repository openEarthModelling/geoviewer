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

Requires Python 3.11+.

```bash
pip install .
```

For an editable install that includes the test/lint tooling:

```bash
pip install -e ".[dev]"
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv pip install .
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

### Natural Earth feature data (first render)

Coastlines, borders and the graticule come from Natural Earth data, which
cartopy downloads on first use and caches in `~/.local/share/cartopy`. Behind
a blocking proxy the download fails; the map still renders, just without the
overlays (a warning names the unavailable features). To pre-seed the cache on
a proxied server, clear the proxy variables and render any map once:

```bash
env -u http_proxy -u https_proxy python -m panel serve app.py --port 5006
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
