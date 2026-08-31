import os

from .base import FormatNotRecognized
from .netcdf import NetCDFReader
from .hdf5 import HDF5Reader
from .grib import GRIBReader

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
    """用文件头魔数判断格式；失败抛 FormatNotRecognized。"""
    with open(path, "rb") as f:
        head = f.read(8)
    if head.startswith(b"GRIB"):
        return "grib"
    if head.startswith(b"\x89HDF\r\n\x1a\n"):
        # HDF5 容器：可能是纯 HDF5 或 netCDF-4。netCDF-4 根 group 带 _NCProperties 属性。
        # 该属性是隐藏属性，netCDF4 的 ncattrs() 不会列出，须用 h5py 的 attrs 判断。
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
    """内容嗅探优先（魔数是权威信号），扩展名作为回退。"""
    try:
        return _sniff(path)
    except FormatNotRecognized:
        ext = os.path.splitext(path)[1].lower()
        if ext in _EXT_MAP:
            return _EXT_MAP[ext]
        raise
