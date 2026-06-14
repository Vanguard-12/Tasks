import os
from pathlib import Path
from typing import Dict, List

from config import OUTPUT_DIR


class VirtualFileSystem:
    """A very small in‑memory file system.

    Files are stored in a dictionary keyed by a *normalized* relative path.
    The ``flush_to_disk`` method writes every stored file into ``OUTPUT_DIR``
    while protecting against path‑traversal attacks.
    """

    def __init__(self) -> None:
        # Mapping of normalized relative POSIX paths -> content
        self._files: Dict[str, str] = {}

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    @staticmethod
    def _normalize_path(path: str) -> str:
        """Return a POSIX‑style relative path without leading ``/``.

        ``..`` components are resolved and any attempt to escape the virtual
        root raises ``ValueError``.
        """
        p = Path(path).as_posix()
        # Remove leading slash to keep it relative
        if p.startswith('/'):
            p = p[1:]
        # Resolve ``..`` and ``.`` – ``Path`` does not resolve without a root,
        # so we prepend a dummy root, resolve, then strip it again.
        resolved = Path('/') / p
        resolved = resolved.resolve().relative_to('/')
        # After resolution, ``..`` should no longer be present.
        if '..' in resolved.parts:
            raise ValueError(f"Invalid path traversal attempt: {path}")
        return resolved.as_posix()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def create_file(self, path: str, content: str) -> None:
        """Create or overwrite a virtual file.

        Parameters
        ----------
        path: str
            Relative path inside the virtual file system (e.g. ``"reports/summary.txt"``).
        content: str
            Text content to store.
        """
        norm_path = self._normalize_path(path)
        self._files[norm_path] = content

    def read_file(self, path: str) -> str:
        """Return the content of a virtual file.

        Raises ``KeyError`` if the file does not exist.
        """
        norm_path = self._normalize_path(path)
        return self._files[norm_path]

    def list_files(self) -> List[str]:
        """Return a list of all virtual file paths (POSIX style)."""
        return list(self._files.keys())

    def flush_to_disk(self, base_dir: Path | None = None) -> None:
        """Write all virtual files to the real file system.

        Files are written under ``base_dir`` (defaults to ``config.OUTPUT_DIR``).
        The directory hierarchy is created as needed.
        """
        target_root = Path(base_dir) if base_dir else OUTPUT_DIR
        for rel_path, content in self._files.items():
            # Resolve the final path safely inside ``target_root``
            final_path = (target_root / rel_path).resolve()
            if not str(final_path).startswith(str(target_root.resolve())):
                raise ValueError(f"Attempted to write outside of output directory: {final_path}")
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_text(content, encoding="utf-8")

    # ---------------------------------------------------------------------
    # Convenience representation
    # ---------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"VirtualFileSystem({len(self._files)} files)"
