from functools import lru_cache

from readers import get_reader, identify


class SliceService:
    def __init__(self, maxsize: int = 16):
        self.maxsize = maxsize
        self._get = lru_cache(maxsize=maxsize)(self._uncached)

    def _key(self, path: str, var_path: str, index: tuple) -> tuple:
        # index is the stable serialization of the slices dict: sorted items
        return (path, var_path, tuple(sorted(index)))

    def _uncached(self, path, var_path, index_tuple):
        reader = get_reader(identify(path))
        return reader.read_slice(path, var_path, dict(index_tuple))

    def get(self, path: str, var_path: str, index: dict):
        # The cache key is (path, var_path, sorted items tuple). lru_cache computes
        # the key from positional args, so unpack them to match _uncached(path, var_path, index_tuple).
        return self._get(*self._key(path, var_path, tuple(index.items())))
