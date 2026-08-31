import netCDF4
import xarray as xr

from .base import Reader, VarInfo, OpenFailed, VariableNotFound, SliceOutOfBounds


def _split_var_path(var_path: str) -> tuple:
    """'/sub/pm' -> ('/sub', 'pm'); 'o3' -> (None, 'o3')。"""
    if "/" not in var_path:
        return None, var_path
    group, _, name = var_path.rpartition("/")
    return group or None, name


class NetCDFReader(Reader):
    format = "netcdf"

    def _walk(self, path: str):
        """递归遍历所有 group，返回 [(var_path, shape, dims)]。"""
        root = netCDF4.Dataset(path, "r")
        out = []

        def walk(grp, prefix):
            for name, var in grp.variables.items():
                vp = f"{prefix}/{name}" if prefix else name
                out.append((vp, var.shape, var.dimensions))
            for name, sub in grp.groups.items():
                walk(sub, f"{prefix}/{name}")

        try:
            walk(root, "")
        finally:
            root.close()
        return out

    def list_variables(self, path: str) -> list[VarInfo]:
        try:
            items = self._walk(path)
        except Exception as e:
            raise OpenFailed(f"failed to open netCDF: {path}: {e}") from e
        return [
            VarInfo(
                path=vp,
                name=vp.rsplit("/", 1)[-1],
                shape=tuple(shape),
                dims=tuple(dims),
                is_plottable=len(shape) >= 2,
                format=self.format,
            )
            for vp, shape, dims in items
        ]

    def read_slice(self, path: str, var_path: str, slices: dict) -> xr.DataArray:
        group, name = _split_var_path(var_path)
        try:
            ds = xr.open_dataset(path, group=group, chunks="auto")
        except Exception as e:
            raise OpenFailed(f"failed to open netCDF: {path}: {e}") from e
        with ds:
            if name not in ds:
                raise VariableNotFound(f"variable not found: {var_path}")
            da = ds[name]
            try:
                out = da.isel(**{k: v for k, v in slices.items() if k in da.dims})
            except (IndexError, KeyError, ValueError) as e:
                raise SliceOutOfBounds(f"slice out of bounds: {slices}: {e}") from e
            result = out.compute()
        return result

    def read_metadata(self, path: str, var_path: str) -> dict:
        group, name = _split_var_path(var_path)
        try:
            ds = xr.open_dataset(path, group=group)
        except Exception as e:
            raise OpenFailed(f"failed to open netCDF: {path}: {e}") from e
        with ds:
            if name not in ds:
                raise VariableNotFound(f"variable not found: {var_path}")
            attrs = dict(ds[name].attrs)
        return attrs
