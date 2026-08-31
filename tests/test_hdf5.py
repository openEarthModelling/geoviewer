import h5py
import numpy as np
import pytest

from readers.base import VariableNotFound, SliceOutOfBounds
from readers.hdf5 import HDF5Reader


@pytest.fixture
def h5_file(tmp_path):
    p = tmp_path / "data.h5"
    with h5py.File(p, "w") as f:
        g = f.create_group("obs")
        d = g.create_dataset("aod", data=np.arange(24).reshape(4, 6))
        d.attrs["units"] = "1"
        f.create_dataset("flat2d", data=np.ones((2, 3)))
    return str(p)


def test_list_variables_group_tree(h5_file):
    r = HDF5Reader()
    infos = r.list_variables(h5_file)
    paths = {i.path for i in infos}
    assert "/obs/aod" in paths
    assert "/flat2d" in paths
    aod = next(i for i in infos if i.path == "/obs/aod")
    assert aod.shape == (4, 6)
    assert aod.dims == ("dim_0", "dim_1")


def test_read_slice(h5_file):
    r = HDF5Reader()
    da = r.read_slice(h5_file, "/obs/aod", {"dim_0": 2})
    assert da.shape == (6,)
    assert da.values[0] == 12  # reshape(4,6)[2,0] = 12


def test_variable_not_found(h5_file):
    r = HDF5Reader()
    with pytest.raises(VariableNotFound):
        r.read_slice(h5_file, "/nope", {})


def test_slice_out_of_bounds(h5_file):
    r = HDF5Reader()
    with pytest.raises(SliceOutOfBounds):
        r.read_slice(h5_file, "/obs/aod", {"dim_0": 99})
