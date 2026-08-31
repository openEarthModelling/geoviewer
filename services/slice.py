from functools import lru_cache

from readers import identify, get_reader


class SliceService:
    def __init__(self, maxsize: int = 16):
        self.maxsize = maxsize
        self._get = lru_cache(maxsize=maxsize)(self._uncached)

    def _key(self, path: str, var_path: str, index: tuple) -> tuple:
        # index 是 slices dict 的稳定序列化：sorted items
        return (path, var_path, tuple(sorted(index)))

    def _uncached(self, path, var_path, index_tuple):
        reader = get_reader(identify(path))
        return reader.read_slice(path, var_path, dict(index_tuple))

    def get(self, path: str, var_path: str, index: dict):
        # 缓存键是 (path, var_path, 排序后的 items tuple)；lru_cache 按位置参数
        # 计算 key，故需解包传入，与 _uncached(path, var_path, index_tuple) 对齐。
        return self._get(*self._key(path, var_path, tuple(index.items())))
