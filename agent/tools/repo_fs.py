from __future__ import annotations

import fnmatch
from pathlib import Path


class RepoFSError(RuntimeError):
    pass


class RepoFS:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()

    def _resolve(self, path: str | Path) -> Path:
        candidate = (self.root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise RepoFSError(f"Path escapes repository root: {path}")
        return candidate

    def _ensure_editable(self, path: Path) -> None:
        if path.name in {".env", ".env.example"}:
            raise RepoFSError(f"Refusing to edit {path.name}.")

    def list_files(self, pattern: str = "*") -> list[str]:
        files: list[str] = []
        for path in self.root.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                rel = path.relative_to(self.root).as_posix()
                if fnmatch.fnmatch(rel, pattern):
                    files.append(rel)
        return sorted(files)

    def read_file(self, path: str | Path) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def write_file(self, path: str | Path, content: str) -> str:
        target = self._resolve(path)
        self._ensure_editable(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
        return target.relative_to(self.root).as_posix()

    def create_directory(self, path: str | Path) -> str:
        target = self._resolve(path)
        self._ensure_editable(target)
        target.mkdir(parents=True, exist_ok=True)
        return target.relative_to(self.root).as_posix()

    def search_files(self, query: str, pattern: str = "*") -> list[dict[str, str | int]]:
        matches: list[dict[str, str | int]] = []
        for rel in self.list_files(pattern):
            path = self._resolve(rel)
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(lines, start=1):
                if query in line:
                    matches.append({"file": rel, "line": number, "text": line})
        return matches

    def apply_patch(self, path: str | Path, old: str, new: str) -> str:
        target = self._resolve(path)
        self._ensure_editable(target)
        content = target.read_text(encoding="utf-8")
        if old not in content:
            raise RepoFSError(f"Patch target text not found in {path}")
        target.write_text(content.replace(old, new, 1), encoding="utf-8", newline="\n")
        return target.relative_to(self.root).as_posix()
