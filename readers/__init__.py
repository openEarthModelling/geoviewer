import os

from .base import FormatNotRecognized
from .grib import GRIBReader
from .hdf5 import HDF5Reader
from .netcdf import NetCDFReader

_READERS = {
    "netcdf": NetCDFReader(),
    "hdf5": HDF5Reader(),
    "grib": GRIBReader(),
}

_EXT_MAP = {
    ".nc": "netcdf", ".nc4": "netcdf", ".cdf": "netcdf",
    ".grib": "grib", ".grb": "grib", ".grib2": "grib", ".grb2": "grib",
    ".h5": "hdf5", ".hdf": "hdf5", ".hdf5": "hdf5", ".he5": "hdf5",
}


def get_reader(fmt: str):
    if fmt not in _READERS:
        raise ValueError(f"Unknown format: {fmt}")
    return _READERS[fmt]


def _sniff(path: str) -> str:
    """Detect format by file magic; raises FormatNotRecognized on failure."""
    with open(path, "rb") as f:
        head = f.read(8)
    if head.startswith(b"GRIB"):
        return "grib"
    if head.startswith(b"\x89HDF\r\n\x1a\n"):
        # HDF5 container: may be plain HDF5 or netCDF-4. The netCDF-4 root group
        # carries a _NCProperties attribute. It is hidden (netCDF4's ncattrs()
        # does not list it), so check via h5py's attrs.
        try:
            import h5py
            with h5py.File(path, "r") as f:
                if "_NCProperties" in f.attrs:
                    return "netcdf"
        except Exception:
            pass
        return "hdf5"
    if head[:3] == b"CDF":
        return "netcdf"
    raise FormatNotRecognized(f"Unrecognized format: {path}")


def identify(path: str) -> str:
    """Content sniffing first (magic is the authoritative signal), extension as fallback."""
    try:
        return _sniff(path)
    except FormatNotRecognized:
        ext = os.path.splitext(path)[1].lower()
        if ext in _EXT_MAP:
            return _EXT_MAP[ext]
        raise
