import h5py
import numpy as np
import xarray as xr

from .base import OpenFailed, Reader, SliceOutOfBounds, VariableNotFound, VarInfo


class HDF5Reader(Reader):
    format = "hdf5"

    def _datasets(self, path: str) -> list[tuple[str, tuple, int]]:
        try:
            f = h5py.File(path, "r")
        except Exception as e:
            raise OpenFailed(f"failed to open HDF5: {path}: {e}") from e
        items = []
        f.visititems(lambda name, obj: items.append(
            (name, tuple(obj.shape), obj.ndim))
            if isinstance(obj, h5py.Dataset) else None)
        f.close()
        return items

    def list_variables(self, path: str) -> list[VarInfo]:
        return [
            VarInfo(
                path=f"/{name}",
                name=name.rsplit("/", 1)[-1],
                shape=shape,
                dims=tuple(f"dim_{i}" for i in range(ndim)),
                is_plottable=ndim >= 2,
                format=self.format,
            )
            for name, shape, ndim in self._datasets(path)
        ]

    def read_slice(self, path: str, var_path: str, slices: dict) -> xr.DataArray:
        name = var_path.lstrip("/")
        try:
            f = h5py.File(path, "r")
        except Exception as e:
            raise OpenFailed(f"failed to open HDF5: {path}: {e}") from e
        if name not in f:
            f.close()
            raise VariableNotFound(f"variable not found: {var_path}")
        ds = f[name]
        idx = []
        for i in range(ds.ndim):
            key = f"dim_{i}"
            if key in slices:
                v = slices[key]
                if v < 0 or v >= ds.shape[i]:
                    f.close()
                    raise SliceOutOfBounds(f"slice out of bounds: {key}={v}")
                idx.append(v)
            else:
                idx.append(slice(None))
        arr = np.asarray(ds[tuple(idx)])
        f.close()
        return xr.DataArray(
            arr,
            dims=tuple(f"dim_{i}" for i in range(arr.ndim)),
            name=var_path.rsplit("/", 1)[-1],
        )

    def read_metadata(self, path: str, var_path: str) -> dict:
        name = var_path.lstrip("/")
        try:
            f = h5py.File(path, "r")
        except Exception as e:
            raise OpenFailed(f"failed to open HDF5: {path}: {e}") from e
        if name not in f:
            f.close()
            raise VariableNotFound(f"variable not found: {var_path}")
        attrs = {k: v for k, v in f[name].attrs.items()}
        f.close()
        return attrs
