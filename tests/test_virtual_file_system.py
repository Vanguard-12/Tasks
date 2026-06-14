import pytest
from pathlib import Path
from virtual_file_system import VirtualFileSystem
from config import OUTPUT_DIR


def test_create_and_read_file(tmp_path: Path):
    vfs = VirtualFileSystem()
    vfs.create_file("folder/example.txt", "Hello World")
    assert vfs.read_file("folder/example.txt") == "Hello World"
    assert vfs.list_files() == ["folder/example.txt"]


def test_path_normalisation_and_security(tmp_path: Path):
    vfs = VirtualFileSystem()
    # Normal relative path works
    vfs.create_file("a/b.txt", "data")
    # Attempt to escape the virtual root should raise
    with pytest.raises(ValueError):
        vfs.create_file("../outside.txt", "bad")
    with pytest.raises(ValueError):
        vfs.read_file("../../etc/passwd")


def test_flush_to_disk(tmp_path: Path):
    # Use a temporary output directory to avoid polluting the repo
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    vfs = VirtualFileSystem()
    vfs.create_file("doc.txt", "sample content")
    vfs.create_file("sub/inner.md", "# Title")
    vfs.flush_to_disk(out_dir)
    # Verify files exist on disk with correct content
    assert (out_dir / "doc.txt").read_text() == "sample content"
    assert (out_dir / "sub" / "inner.md").read_text() == "# Title"


def test_flush_prevents_path_traversal(tmp_path: Path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    vfs = VirtualFileSystem()
    vfs.create_file("good.txt", "ok")
    # Manually inject a malicious path (bypassing create_file validation)
    vfs._files["../evil.txt"] = "malicious"
    with pytest.raises(ValueError):
        vfs.flush_to_disk(out_dir)
