import os
from dataclasses import dataclass


class PathOutsideWhitelist(Exception):
    """Raised when a relative path resolves outside the whitelisted roots."""
    pass


@dataclass
class Entry:
    name: str
    path: str     # path relative to the whitelist root
    is_dir: bool


class Catalog:
    """Directory whitelist: only allows browsing beneath the given roots, with path-traversal protection."""

    def __init__(self, roots: list[str]):
        self.roots = [os.path.realpath(r) for r in roots]

    def resolve(self, rel_path: str) -> str:
        """Resolve a relative path under one of the roots; raises PathOutsideWhitelist if outside."""
        # Do not lstrip("/"): absolute paths (e.g. /etc/passwd) must be judged as
        # absolute, otherwise they would be joined under a root and treated as
        # inside it, bypassing the whitelist.
        # Use realpath to resolve symlinks, so an in-root symlink cannot point outside.
        for root in self.roots:
            full = os.path.realpath(os.path.join(root, rel_path))
            if full == root or full.startswith(root + os.sep):
                return full
        raise PathOutsideWhitelist(f"path outside whitelist: {rel_path}")

    def to_rel(self, path: str) -> str:
        """Normalize an absolute or relative path to a whitelisted relative path (root is ""); raises PathOutsideWhitelist if outside."""
        if not path:
            return ""
        full = self.resolve(path)
        for root in self.roots:
            if full == root:
                return ""
            if full.startswith(root + os.sep):
                return os.path.relpath(full, root)
        raise PathOutsideWhitelist(f"path outside whitelist: {path}")

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
