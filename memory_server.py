import json
import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict

from fastmcp import FastMCP


class MemoryServer:
    """Helper class that encapsulates JSON‑file storage logic.

    The class does **not** depend on FastMCP directly – it only provides
    low‑level CRUD helpers that are later exposed as MCP tools.
    """

    def __init__(self, storage_path: str = "./memory_data.json") -> None:
        self.storage_path = Path(storage_path)
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _load_memory(self) -> Dict[str, Dict[str, Any]]:
        """Load the whole memory dictionary from the JSON file.

        Returns
        -------
        dict
            Mapping ``storage_key -> {"value": ..., "timestamp": ...}``
        """
        if not self.storage_path.exists():
            return {}
        try:
            with self.storage_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file – start fresh
            return {}

    def _save_memory(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Persist *data* to the JSON file.

        The function overwrites the whole file atomically (via ``Path.write_text``).
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _validate_key(key: str) -> bool:
        """Very small validation – reject characters that could be used for path‑traversal.

        Returns ``True`` if the key is safe, ``False`` otherwise.
        """
        # Disallow '/', '\\' and ".." sequences
        unsafe = ["/", "\\", ".."]
        return not any(part in key for part in unsafe)

    # ---------------------------------------------------------------------
    # Public API used by the MCP tools
    # ---------------------------------------------------------------------
    def save(self, key: str, value: Any, namespace: str = "default") -> bool:
        if not self._validate_key(key) or not self._validate_key(namespace):
            return False
        storage_key = f"{namespace}:{key}" if namespace else key
        data = self._load_memory()
        data[storage_key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._save_memory(data)
        return True

    def get(self, key: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        if not self._validate_key(key) or not self._validate_key(namespace):
            return None
        storage_key = f"{namespace}:{key}" if namespace else key
        data = self._load_memory()
        entry = data.get(storage_key)
        if entry is None:
            return None
        return {
            "key": storage_key,
            "value": entry["value"],
            "timestamp": entry["timestamp"]
        }

    def delete(self, key: str, namespace: str = "default") -> bool:
        if not self._validate_key(key) or not self._validate_key(namespace):
            return False
        storage_key = f"{namespace}:{key}" if namespace else key
        data = self._load_memory()
        if storage_key in data:
            del data[storage_key]
            self._save_memory(data)
            return True
        return False

    def list_keys(self, pattern: str = "*") -> List[str]:
        data = self._load_memory()
        all_keys = list(data.keys())
        return [k for k in all_keys if fnmatch.fnmatch(k, pattern)]

    def get_by_namespace(self, namespace: str = "default") -> List[Dict[str, Any]]:
        prefix = f"{namespace}:" if namespace else ""
        data = self._load_memory()
        result: List[Dict[str, Any]] = []
        for storage_key, entry in data.items():
            if storage_key.startswith(prefix):
                result.append({
                    "key": storage_key,
                    "value": entry["value"],
                    "timestamp": entry["timestamp"]
                })
        return result


# -------------------------------------------------------------------------
# MCP server definition – tools are exposed at module level using a single
# FastMCP instance.  The ``MemoryServer`` instance above is used to perform the
# actual storage work.
# -------------------------------------------------------------------------

mcp = FastMCP("Memory-Server")
_storage = MemoryServer()


@mcp.tool()
def save(key: str, value: Any) -> bool:
    """Save *value* under *key* in the default namespace.

    Returns ``True`` on success, ``False`` otherwise (e.g. validation failure).
    """
    return _storage.save(key, value, namespace="default")


@mcp.tool()
def get(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve a record from the default namespace.

    If the key does not exist ``None`` is returned.
    """
    return _storage.get(key, namespace="default")


@mcp.tool()
def delete(key: str) -> bool:
    """Delete *key* from the default namespace.

    Returns ``True`` if the key existed and was removed, ``False`` otherwise.
    """
    return _storage.delete(key, namespace="default")


@mcp.tool()
def list_keys(pattern: str = "*") -> List[str]:
    """List all stored keys (including namespace prefixes) matching *pattern*.

    ``*`` and ``?`` wildcards are supported via :pymod:`fnmatch`.
    """
    return _storage.list_keys(pattern)


@mcp.tool()
def save_with_namespace(key: str, value: Any, namespace: str = "default") -> bool:
    """Save *value* under *key* inside the specified *namespace*.

    The underlying storage key is ``"{namespace}:{key}"``.
    """
    return _storage.save(key, value, namespace=namespace)


@mcp.tool()
def get_by_namespace(namespace: str = "default") -> List[Dict[str, Any]]:
    """Return all records that belong to *namespace*.

    The result is a list of dictionaries with the fields ``key``, ``value`` and
    ``timestamp``.
    """
    return _storage.get_by_namespace(namespace)


if __name__ == "__main__":
    # Run the MCP server on stdio – this is the transport required by the
    # assignment.  ``show_banner=False`` gives a clean output for the client.
    mcp.run(transport="stdio", show_banner=False, log_level="ERROR")
