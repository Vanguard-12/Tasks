import sys
from typing import Any

from config import config
from virtual_fs import VirtualFileSystem
from search_tool import search


def _create_virtual_file(vfs: VirtualFileSystem, path: str, content: str) -> None:
    """Helper that writes *content* to *path* inside the provided virtual FS."""
    vfs.write(path, content)


def run_interactive() -> None:
    """Simple interactive loop demonstrating the DeepAgent capabilities.

    The flow is intentionally straightforward:

    1. Prompt the user for a natural‑language query.
    2. Perform a web search using :func:`search_tool.search`.
    3. Store the raw search result in a virtual file called ``search_result.txt``.
    4. Generate a tiny *summary* (for demo purposes we just prepend a header).
    5. Store the summary in ``summary.md``.
    6. Dump the virtual file system to ``config.output_dir``.
    """
    vfs = VirtualFileSystem()
    try:
        query = input("Enter your query (or press Enter to quit): ").strip()
        if not query:
            print("No query provided – exiting.")
            return
        print("🔎 Performing web search…")
        result = search(query)
        _create_virtual_file(vfs, "search_result.txt", result)
        summary = f"# Summary for query: {query}\n\n{result}\n"
        _create_virtual_file(vfs, "summary.md", summary)
        print(f"🗂 Writing virtual files to '{config.output_dir}' …")
        vfs.dump(config.output_dir)
        print("✅ Done. Files written:")
        for f in vfs.list_files():
            print(f" - {f}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}", file=sys.stderr)


if __name__ == "__main__":
    run_interactive()
