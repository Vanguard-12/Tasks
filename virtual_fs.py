import os
from pathlib import Path
from typing import Dict

class VirtualFileSystem:
    """In‑memory virtual file system that can be exported to disk."""

    def __init__(self, export_dir: str = "output_files"):
        self.files: Dict[str, str] = {}
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def write_file(self, filename: str, content: str) -> None:
        self.files[filename] = content

    def read_file(self, filename: str) -> str:
        return self.files.get(filename, "")

    def list_files(self) -> list[str]:
        return list(self.files.keys())

    def export_to_disk(self) -> None:
        for filename, content in self.files.items():
            file_path = self.export_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
