import netCDF4
import numpy as np
import pytest

from readers.base import VariableNotFound, SliceOutOfBounds
from readers.netcdf import NetCDFReader


@pytest.fixture
def nc_flat(tmp_path):
    """扁平根 group 的 netCDF，含 lat/lon/time/lev 4 维变量。"""
    p = tmp_path / "flat.nc"
    ds = netCDF4.Dataset(p, "w")
    ds.createDimension("time", 3)
    ds.createDimension("lev", 2)
    ds.createDimension("lat", 4)
    ds.createDimension("lon", 5)
    v = ds.createVariable("o3", "f8", ("time", "lev", "lat", "lon"))
    v[:] = np.arange(3 * 2 * 4 * 5).reshape(3, 2, 4, 5)
    v.units = "mol mol-1"
    ds.close()
    return str(p)


@pytest.fixture
def nc_group(tmp_path):
    """带嵌套 group 的 netCDF-4。"""
    p = tmp_path / "group.nc"
    ds = netCDF4.Dataset(p, "w")
    g = ds.createGroup("sub")
    g.createDimension("x", 3)
    g.createDimension("y", 4)
    v = g.createVariable("pm", "f8", ("x", "y"))
    v[:] = np.arange(12).reshape(3, 4)
    ds.close()
    return str(p)


def test_list_variables_flat(nc_flat):
    r = NetCDFReader()
    infos = r.list_variables(nc_flat)
    assert len(infos) == 1
    assert infos[0].path == "o3"
    assert infos[0].shape == (3, 2, 4, 5)
    assert infos[0].dims == ("time", "lev", "lat", "lon")


def test_list_variables_group(nc_group):
    r = NetCDFReader()
    infos = r.list_variables(nc_group)
    assert [i.path for i in infos] == ["/sub/pm"]


def test_read_slice(nc_flat):
    r = NetCDFReader()
    da = r.read_slice(nc_flat, "o3", {"time": 1, "lev": 0})
    assert da.shape == (4, 5)
    assert da.values[0, 0] == 40  # o3[1,0,0,0] = 1*(2*4*5) = 40


def test_variable_not_found(nc_flat):
    r = NetCDFReader()
    with pytest.raises(VariableNotFound):
        r.read_slice(nc_flat, "nope", {})


def test_slice_out_of_bounds(nc_flat):
    r = NetCDFReader()
    with pytest.raises(SliceOutOfBounds):
        r.read_slice(nc_flat, "o3", {"time": 99})


def test_read_slice_with_string_var(tmp_path):
    """含 char 字符串变量的文件：read_slice 数值变量不因 dask auto-rechunk 崩溃。

    回归：CESM2/CAM 文件含 object/char 字符串变量时，chunks='auto' 会抛
    NotImplementedError（无法估算 object dtype 大小）。chunks=None 应正常读取。
    """
    p = tmp_path / "with_str.nc"
    ds = netCDF4.Dataset(p, "w")
    ds.createDimension("time", 2)
    ds.createDimension("lat", 3)
    ds.createDimension("lon", 4)
    ds.createDimension("nchar", 12)
    sv = ds.createVariable("description", "S1", ("nchar",))
    sv[:] = np.array(list("temperature!"), dtype="S1")
    v = ds.createVariable("t2m", "f8", ("time", "lat", "lon"))
    v[:] = np.arange(24).reshape(2, 3, 4)
    ds.close()

    r = NetCDFReader()
    da = r.read_slice(str(p), "t2m", {"time": 0})
    assert da.shape == (3, 4)
    assert da.values[0, 0] == 0.0
    assert da.values[2, 3] == 11.0
