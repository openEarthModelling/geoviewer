import eccodes
import xarray as xr

from .base import Reader, VarInfo, OpenFailed, VariableNotFound


class GRIBReader(Reader):
    format = "grib"

    def _messages(self, path: str) -> list[tuple[str, str, int]]:
        """Enumerate every GRIB message's (shortName, typeOfLevel, level)."""
        out = []
        try:
            f = open(path, "rb")
        except OSError as e:
            raise OpenFailed(f"failed to open GRIB: {path}: {e}") from e
        with f:
            while True:
                try:
                    gid = eccodes.codes_grib_new_from_file(f)
                except Exception as e:
                    raise OpenFailed(f"failed to open GRIB: {path}: {e}") from e
                if gid is None:
                    break
                try:
                    out.append((
                        eccodes.codes_get(gid, "shortName"),
                        eccodes.codes_get(gid, "typeOfLevel"),
                        int(eccodes.codes_get(gid, "level")),
                    ))
                finally:
                    eccodes.codes_release(gid)
        return out

    def _split(self, var_path: str) -> tuple[str, str, int]:
        """'shortName/typeOfLevel/level' -> (shortName, typeOfLevel, level)."""
        parts = var_path.split("/")
        if len(parts) != 3:
            raise VariableNotFound(f"invalid GRIB var_path: {var_path}")
        short, typ, lvl = parts
        try:
            return short, typ, int(lvl)
        except ValueError as e:
            raise VariableNotFound(f"invalid GRIB var_path: {var_path}") from e

    def list_variables(self, path: str) -> list[VarInfo]:
        seen = set()
        infos = []
        for short, typ, lvl in self._messages(path):
            vp = f"{short}/{typ}/{lvl}"
            if vp in seen:
                continue
            seen.add(vp)
            infos.append(VarInfo(
                path=vp,
                name=short,
                shape=(),          # GRIB shape is known only after read
                dims=(),
                is_plottable=True,
                format=self.format,
            ))
        return infos

    def read_slice(self, path: str, var_path: str, slices: dict) -> xr.DataArray:
        short, typ, lvl = self._split(var_path)
        try:
            ds = xr.open_dataset(
                path,
                engine="cfgrib",
                backend_kwargs={
                    "filter_by_keys": {
                        "shortName": short,
                        "typeOfLevel": typ,
                        "level": lvl,
                    },
                    "indexpath": "",
                },
            )
        except Exception as e:
            raise OpenFailed(f"failed to read GRIB message: {var_path}: {e}") from e
        # cfgrib may rename the variable (e.g. shortName "2t" -> cf name "t2m"),
        # so fall back to the first data variable when `short` is not present.
        da = ds[short] if short in ds else next(iter(ds.data_vars.values()), None)
        if da is None:
            raise VariableNotFound(f"variable not found: {var_path}")
        return da.compute()

    def read_metadata(self, path: str, var_path: str) -> dict:
        short, typ, lvl = self._split(var_path)
        for s, t, l in self._messages(path):
            if (s, t, l) == (short, typ, lvl):
                return {"shortName": short, "typeOfLevel": typ, "level": lvl}
        raise VariableNotFound(f"variable not found: {var_path}")
