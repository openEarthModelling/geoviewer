import netCDF4
import numpy as np
import pytest

from services.slice import SliceService


@pytest.fixture
def nc(tmp_path):
    p = tmp_path / "a.nc"
    ds = netCDF4.Dataset(p, "w")
    ds.createDimension("time", 3)
    ds.createDimension("y", 2)
    ds.createDimension("x", 2)
    v = ds.createVariable("v", "f8", ("time", "y", "x"))
    v[:] = np.arange(12).reshape(3, 2, 2)
    ds.close()
    return str(p)


def test_get(nc):
    svc = SliceService(maxsize=2)
    da = svc.get(nc, "v", {"time": 1})
    assert da.shape == (2, 2)
    assert da.values[0, 0] == 4


def test_cache_hit(nc):
    svc = SliceService(maxsize=2)
    a = svc.get(nc, "v", {"time": 0})
    b = svc.get(nc, "v", {"time": 0})
    assert a is b  # 命中缓存，同一对象
