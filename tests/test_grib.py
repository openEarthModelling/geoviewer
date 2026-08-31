import eccodes
import numpy as np
import pytest

from readers.base import VariableNotFound
from readers.grib import GRIBReader


def _write_grib(path):
    """Write one 2-metre temperature GRIB2 message (shortName ``2t``).

    eccodes derives ``shortName`` from parameter + level, so ``2t`` implies
    ``typeOfLevel=heightAboveGround`` / ``level=2``. Setting ``surface`` /
    ``level=0`` would re-derive ``shortName`` back to ``t`` (surface
    temperature), so we use the 2m definition to keep the field named ``2t``.
    """
    with open(path, "wb") as out:
        gid = eccodes.codes_grib_new_from_samples("GRIB2")
        eccodes.codes_set(gid, "shortName", "2t")
        eccodes.codes_set(gid, "typeOfLevel", "heightAboveGround")
        eccodes.codes_set(gid, "level", 2)
        eccodes.codes_set(gid, "Ni", 4)
        eccodes.codes_set(gid, "Nj", 3)
        eccodes.codes_set_values(gid, np.arange(12, dtype=np.float64))
        eccodes.codes_write(gid, out)
        eccodes.codes_release(gid)


@pytest.fixture
def grib_file(tmp_path):
    p = tmp_path / "t2m.grib"
    _write_grib(str(p))
    return str(p)


def test_list_variables(grib_file):
    r = GRIBReader()
    infos = r.list_variables(grib_file)
    assert len(infos) >= 1
    assert any(i.name == "2t" for i in infos)


def test_read_slice(grib_file):
    r = GRIBReader()
    infos = r.list_variables(grib_file)
    da = r.read_slice(grib_file, infos[0].path, {})
    assert da.ndim == 2
    assert da.shape == (3, 4)
    assert da.values[0, 0] == 0.0


def test_read_metadata(grib_file):
    r = GRIBReader()
    infos = r.list_variables(grib_file)
    md = r.read_metadata(grib_file, infos[0].path)
    assert md["shortName"] == "2t"
    assert md["typeOfLevel"] == "heightAboveGround"
    assert md["level"] == 2


def test_variable_not_found(grib_file):
    r = GRIBReader()
    with pytest.raises(VariableNotFound):
        r.read_slice(grib_file, "nope/surface/0", {})
