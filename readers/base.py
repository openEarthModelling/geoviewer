from dataclasses import dataclass
from typing import Protocol

import xarray as xr


class ReaderError(Exception):
    """Unified exception base class for the readers layer."""


class FormatNotRecognized(ReaderError):
    pass


class OpenFailed(ReaderError):
    pass


class VariableNotFound(ReaderError):
    pass


class SliceOutOfBounds(ReaderError):
    pass


@dataclass
class VarInfo:
    path: str                 # unique id; netCDF/HDF5 use '/group/var', GRIB uses 'short/typeOfLevel/level'
    name: str                 # display name
    shape: tuple              # variable shape
    dims: tuple               # dimension names
    is_plottable: bool        # whether plottable (ndim >= 2)
    format: str               # 'netcdf' | 'hdf5' | 'grib'


class Reader(Protocol):
    """Unified multi-format reader protocol. All three implementations follow this interface."""
    format: str

    def list_variables(self, path: str) -> list[VarInfo]: ...

    def read_slice(self, path: str, var_path: str, slices: dict) -> xr.DataArray: ...

    def read_metadata(self, path: str, var_path: str) -> dict: ...
