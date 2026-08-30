from dataclasses import dataclass
from typing import Protocol

import xarray as xr


class ReaderError(Exception):
    """readers 层统一异常基类。"""


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
    path: str                 # 唯一标识；netCDF/HDF5 用 '/group/var'，GRIB 用 'short/typeOfLevel/level'
    name: str                 # 展示名
    shape: tuple              # 变量形状
    dims: tuple               # 维度名
    is_plottable: bool        # 是否可绘制（ndim >= 2）
    format: str               # 'netcdf' | 'hdf5' | 'grib'


class Reader(Protocol):
    """多格式读取统一协议。三个实现类都遵守此接口。"""
    format: str

    def list_variables(self, path: str) -> list[VarInfo]: ...

    def read_slice(self, path: str, var_path: str, slices: dict) -> xr.DataArray: ...

    def read_metadata(self, path: str, var_path: str) -> dict: ...
