import h5py
import netCDF4
import numpy as np
import pytest

from readers import identify, get_reader
from readers.base import FormatNotRecognized


def _make_nc(path):
    ds = netCDF4.Dataset(path, "w")
    ds.createDimension("x", 2)
    v = ds.createVariable("v", "f8", ("x",))
    v[:] = [1, 2]
    ds.close()


def _make_h5(path):
    with h5py.File(path, "w") as f:
        f.create_dataset("d", data=np.ones((2, 2)))


def test_identify_by_extension_nc(tmp_path):
    p = tmp_path / "a.nc"
    _make_nc(str(p))
    assert identify(str(p)) == "netcdf"


def test_identify_by_extension_h5(tmp_path):
    p = tmp_path / "a.h5"
    _make_h5(str(p))
    assert identify(str(p)) == "hdf5"


def test_identify_wrong_extension_sniffs(tmp_path):
    """Extension is .h5 but the content is netCDF; sniffing corrects it."""
    p = tmp_path / "actually.nc4.h5"
    _make_nc(str(p))
    assert identify(str(p)) == "netcdf"


def test_identify_unknown(tmp_path):
    p = tmp_path / "data.bin"
    p.write_bytes(b"not a known format")
    with pytest.raises(FormatNotRecognized):
        identify(str(p))


def test_get_reader():
    assert get_reader("netcdf").format == "netcdf"
    assert get_reader("hdf5").format == "hdf5"
    assert get_reader("grib").format == "grib"
    with pytest.raises(ValueError):
        get_reader("bogus")
