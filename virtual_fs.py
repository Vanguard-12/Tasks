import os
from typing import Dict, List

class VirtualFileSystem:
    """A lightweight in‑memory virtual file system.

    Files are stored in a dictionary mapping a *relative* path (as a string)
    to its textual content. The :meth:`dump` method writes all stored files to
    a real directory on disk, preserving any sub‑directory structure encoded
    in the path.
    """

    def __init__(self) -> None:
        self._files: Dict[str, str] = {}

    def write(self, path: str, content: str) -> None:
        """Create or overwrite a virtual file.

        Parameters
        ----------
        path: str
            Relative path (e.g. ``"reports/summary.md"``).
        content: str
            Textual content to store.
        """
        self._files[path] = content

    def read(self, path: str) -> str | None:
        """Return the content of a virtual file or ``None`` if it does not exist."""
        return self._files.get(path)

    def list_files(self) -> List[str]:
        """Return a list of all virtual file paths currently stored."""
        return list(self._files.keys())

    def dump(self, output_dir: str) -> None:
        """Persist all virtual files to the real filesystem.

        The method creates ``output_dir`` if it does not exist and writes each
        virtual file to ``output_dir/<path>``. Sub‑directories are created as
        needed.
        """
        os.makedirs(output_dir, exist_ok=True)
        for rel_path, content in self._files.items():
            full_path = os.path.join(output_dir, rel_path)
            # Ensure the directory hierarchy exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
