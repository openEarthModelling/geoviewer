import os
from dataclasses import dataclass


class PathOutsideWhitelist(Exception):
    """相对路径解析结果越出白名单根目录时抛出。"""
    pass


@dataclass
class Entry:
    name: str
    path: str     # 相对根的白名单内路径
    is_dir: bool


class Catalog:
    """目录白名单：仅允许浏览给定根路径之下的内容，并防御路径穿越。"""

    def __init__(self, roots: list[str]):
        self.roots = [os.path.realpath(r) for r in roots]

    def resolve(self, rel_path: str) -> str:
        """把相对路径解析到某个根下；越界抛 PathOutsideWhitelist。"""
        # 不能 lstrip("/")：绝对路径（如 /etc/passwd）必须按绝对路径判定，
        # 否则会被拼到根下当成根内相对路径，绕过白名单。
        # 用 realpath 解析 symlink，防止根内 symlink 指向白名单外目标。
        for root in self.roots:
            full = os.path.realpath(os.path.join(root, rel_path))
            if full == root or full.startswith(root + os.sep):
                return full
        raise PathOutsideWhitelist(f"path outside whitelist: {rel_path}")

    def list_dir(self, rel_path: str) -> list[Entry]:
        base = self.resolve(rel_path)
        if not os.path.isdir(base):
            return []
        entries = []
        for name in sorted(os.listdir(base)):
            full = os.path.join(base, name)
            entries.append(Entry(
                name=name,
                path=(rel_path.rstrip("/") + "/" + name).lstrip("/"),
                is_dir=os.path.isdir(full),
            ))
        return entries
