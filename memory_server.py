import json
import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List

from fastmcp import FastMCP


class MemoryServer:
    """MCP server that provides simple key‑value memory with namespace support.

    All values are persisted to a JSON file (``memory_data.json``) with a UTC
    ISO‑8601 timestamp. Keys are validated to avoid path‑traversal characters.
    """

    # Class‑level MCP instance so that decorators can reference it at import time
    mcp = FastMCP("Memory-Server")

    def __init__(self) -> None:
        # Instance attributes
        self.storage_path = Path("./memory_data.json")
        # Expose the class‑level MCP instance via the instance for run()
        self.mcp = self.__class__.mcp

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _load_memory(self) -> dict:
        """Load the whole memory dictionary from ``self.storage_path``.

        Returns an empty dict if the file does not exist or is empty.
        """
        if not self.storage_path.exists():
            return {}
        try:
            with self.storage_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file – start fresh
            return {}

    def _save_memory(self, data: dict) -> None:
        """Atomically write *data* to ``self.storage_path``.

        The parent directory is created if necessary.
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temporary file then rename for atomicity
        temp_path = self.storage_path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(self.storage_path)

    def _validate_key(self, key: str) -> None:
        """Raise ``ValueError`` if *key* contains unsafe characters.

        Disallowed patterns: ``/``, ``\\``, ``..`` (any occurrence), empty string.
        """
        if not key:
            raise ValueError("Key must be a non‑empty string")
        if "/" in key or "\\" in key or ".." in key:
            raise ValueError(f"Invalid key '{key}': contains prohibited characters")

    # ---------------------------------------------------------------------
    # MCP tools
    # ---------------------------------------------------------------------
    @mcp.tool()
    def save(self, key: str, value: Any) -> bool:
        """Save *value* under *key*.

        The entry is stored as ``{"value": <value>, "timestamp": <ISO‑8601>}``.
        Returns ``True`` on success, ``False`` on validation error.
        """
        try:
            self._validate_key(key)
        except ValueError:
            return False
        data = self._load_memory()
        data[key] = {"value": value, "timestamp": datetime.utcnow().isoformat()}
        self._save_memory(data)
        return True

    @mcp.tool()
    def get(self, key: str) -> Optional[dict]:
        """Retrieve the entry for *key*.

        Returns a dictionary ``{"key": key, "value": ..., "timestamp": ...}``
        or ``None`` if the key does not exist.
        """
        try:
            self._validate_key(key)
        except ValueError:
            return None
        data = self._load_memory()
        entry = data.get(key)
        if entry is None:
            return None
        return {"key": key, "value": entry.get("value"), "timestamp": entry.get("timestamp")}

    @mcp.tool()
    def delete(self, key: str) -> bool:
        """Delete *key* from memory.

        Returns ``True`` if the key existed and was removed, ``False`` otherwise.
        """
        try:
            self._validate_key(key)
        except ValueError:
            return False
        data = self._load_memory()
        if key in data:
            del data[key]
            self._save_memory(data)
            return True
        return False

    @mcp.tool()
    def list_keys(self, pattern: str = "*") -> List[str]:
        """Return a list of all keys matching *pattern*.

        ``pattern`` supports ``*`` and ``?`` wildcards as interpreted by
        :func:`fnmatch.fnmatch`.
        """
        data = self._load_memory()
        return [k for k in data.keys() if fnmatch.fnmatch(k, pattern)]

    @mcp.tool()
    def save_with_namespace(self, key: str, value: Any, namespace: str = "default") -> bool:
        """Save *value* under a namespaced key.

        The composite key is ``f"{namespace}:{key}"``. Validation is applied to
        both *namespace* and *key*.
        """
        try:
            self._validate_key(key)
            self._validate_key(namespace)
        except ValueError:
            return False
        composite_key = f"{namespace}:{key}"
        data = self._load_memory()
        data[composite_key] = {"value": value, "timestamp": datetime.utcnow().isoformat()}
        self._save_memory(data)
        return True

    @mcp.tool()
    def get_by_namespace(self, namespace: str = "default") -> List[dict]:
        """Return all entries that belong to *namespace*.

        Each item in the returned list is a dictionary with ``key`` (the full
        ``namespace:key`` string), ``value`` and ``timestamp``.
        """
        try:
            self._validate_key(namespace)
        except ValueError:
            return []
        prefix = f"{namespace}:"
        data = self._load_memory()
        result: List[dict] = []
        for k, v in data.items():
            if k.startswith(prefix):
                result.append({"key": k, "value": v.get("value"), "timestamp": v.get("timestamp")})
        return result


# -------------------------------------------------------------------------
# Server entry point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    server = MemoryServer()
    server.mcp.run(
        transport="stdio",
        show_banner=False,
        log_level="ERROR",
    )
