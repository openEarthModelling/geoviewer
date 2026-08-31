from dataclasses import dataclass, field


@dataclass
class RoleAssignment:
    x: str | None = None
    y: str | None = None
    z: str | None = None
    time: str | None = None
    fixed: dict = field(default_factory=dict)


# Naming heuristics (lowercased). y=latitude first, x=longitude first, z=height, time=time.
_LAT = ("lat", "latitude", "latitudes", "south_north", "nav_lat", "rlat")
_LON = ("lon", "longitude", "longitudes", "west_east", "nav_lon", "rlon")
_Z = ("lev", "level", "height", "altitude", "z", "plev", "pres", "isobaricinhpa")
_TIME = ("time", "t", "datetime", "date", "valid_time", "forecast_time")


def auto_assign(dims: list, units: dict | None = None) -> RoleAssignment:
    """Assign dimension roles via naming heuristics with a units fallback. dims is the list of dimension names."""
    ra = RoleAssignment()
    units = units or {}
    for d in dims:
        dl = str(d).lower()
        if ra.y is None and dl in _LAT:
            ra.y = d
        elif ra.x is None and dl in _LON:
            ra.x = d
        elif ra.z is None and dl in _Z:
            ra.z = d
        elif ra.time is None and dl in _TIME:
            ra.time = d
    # units fallback
    for d in dims:
        u = str(units.get(d, ""))
        if "degrees_north" in u and ra.y is None:
            ra.y = d
        if "degrees_east" in u and ra.x is None:
            ra.x = d
    return ra
