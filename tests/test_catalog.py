import os

import pytest

from services.catalog import Catalog, PathOutsideWhitelist


@pytest.fixture
def cat(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.nc").write_bytes(b"x")
    (tmp_path / "b.grib").write_bytes(b"x")
    return Catalog([str(tmp_path)])


def test_list_dir(cat, tmp_path):
    entries = cat.list_dir("")
    names = {e.name for e in entries}
    assert "sub" in names
    assert "b.grib" in names


def test_resolve_ok(cat, tmp_path):
    p = cat.resolve("sub/a.nc")
    assert p == str(tmp_path / "sub" / "a.nc")


def test_resolve_traversal_blocked(cat):
    with pytest.raises(PathOutsideWhitelist):
        cat.resolve("../etc/passwd")


def test_resolve_outside_blocked(cat):
    with pytest.raises(PathOutsideWhitelist):
        cat.resolve("/etc/passwd")


def test_resolve_symlink_escape_blocked(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_bytes(b"x")
    os.symlink(outside, root / "link")
    with pytest.raises(PathOutsideWhitelist):
        Catalog([str(root)]).resolve("link/secret.txt")
