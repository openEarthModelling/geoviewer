from services.dimension import auto_assign


def test_auto_assign_standard():
    ra = auto_assign(["time", "lev", "lat", "lon"])
    assert ra.x == "lon"
    assert ra.y == "lat"
    assert ra.z == "lev"
    assert ra.time == "time"


def test_auto_assign_weird_names():
    ra = auto_assign(["t", "height", "south_north", "west_east"])
    assert ra.y == "south_north"
    assert ra.x == "west_east"
    assert ra.z == "height"


def test_auto_assign_no_latlon():
    ra = auto_assign(["time", "x"])
    assert ra.y is None
    assert ra.time == "time"


def test_auto_assign_units_fallback():
    ra = auto_assign(["a", "b"], units={"a": "degrees_north", "b": "degrees_east"})
    assert ra.y == "a"
    assert ra.x == "b"


def test_role_assignment_fixed():
    ra = auto_assign(["time", "lev", "lat", "lon"])
    ra.fixed = {"lev": 0}
    assert ra.fixed == {"lev": 0}
