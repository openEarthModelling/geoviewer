import pytest

from readers.base import (
    ReaderError, FormatNotRecognized, OpenFailed,
    VariableNotFound, SliceOutOfBounds, VarInfo,
)


def test_exception_hierarchy():
    assert issubclass(FormatNotRecognized, ReaderError)
    assert issubclass(OpenFailed, ReaderError)
    assert issubclass(VariableNotFound, ReaderError)
    assert issubclass(SliceOutOfBounds, ReaderError)


def test_varinfo_fields():
    v = VarInfo(path="/g/v", name="v", shape=(3, 4), dims=("x", "y"),
                is_plottable=True, format="netcdf")
    assert v.path == "/g/v"
    assert v.shape == (3, 4)
    assert v.dims == ("x", "y")
    assert v.is_plottable is True
    assert v.format == "netcdf"
